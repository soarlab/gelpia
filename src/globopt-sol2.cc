#include <boost/numeric/interval.hpp>
#include <vector>
#include <queue>
#include <cmath>
#include <iostream>
#include <functional>
#include <cassert>
#include <mutex>
#include <thread>
#include <atomic>
#include <algorithm>
#include "helpers.h"
#include "harness.h"

using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/* Global queue */
static vector<double> f_best_highs;
static vector<std::queue<box_t>> Qs;

void sol2_worker(double x_tol, double f_tol, int max_iter,
		 const function<interval<double>(const box_t &)> & F, int i);

vector<box_t> multi_split(const box_t & X)
{
  vector<box_t> retval(num_threads, X);

  // Split the box along longest dimension
  double longest = 0.0;
  int longest_idx = 0;
  for(uint i = 0; i < X.size(); ++i) {
    if(width(X[i]) > longest) {
      longest = width(X[i]);
      longest_idx = i;
    }
  }

  double step = width(X[longest_idx])/num_threads;
  for (int i=0; i< retval.size(); i++) {
    retval[i][longest_idx].assign(X[longest_idx].lower() + i*step, X[longest_idx].lower() + (i+1)*step);
  }

  return retval;
}

double sol2_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter,
		   const function<interval<double>(const box_t &)> & F)
{
  Qs = std::vector<std::queue<box_t>>(num_threads);
  f_best_highs = std::vector<double>(num_threads);
  
  vector<box_t> parts = multi_split(X_0);

  // Create threads
  std::vector<std::thread> threads;
  for(int i = 0; i < num_threads; ++i) {
    std::queue<box_t> Q;
    Q.push(parts[i]);
    Qs[i] = Q;
    f_best_highs[i] = -INFINITY;
  }
    for(int i = 0; i < num_threads; ++i) {
    threads.push_back(std::thread(sol2_worker, x_tol, f_tol, max_iter, std::ref(F), i));
  }

  // Wait
  for(auto & t : threads)
    t.join();
  // Return result
  double max = -INFINITY;
  for(auto val : f_best_highs) {
    if(max < val)
      max = val;
  }
  return max;
}

/*
 * Global maximum solver
 * Arguments:
 *          X_0      - given starting box
 *          x_tol    -
 *          f_tol    -
 *          max_iter - maximum iterations
 *          F        - function to fin maximum of
 */
void sol2_worker(double x_tol, double f_tol, int max_iter,
		 const function<interval<double>(const box_t &)> & F,
		 int my_index)
{
  int iter_count = 0;
  double f_best_low = -INFINITY;
  while(!Qs[my_index].empty()) {
    // grab new work item
    box_t X = Qs[my_index].front();
    Qs[my_index].pop();

    interval<double> f = F(X);
    double w = width(X);
    double fw = width(f);

    if(f.upper() < f_best_low
       || w <= x_tol
       || fw <= f_tol
       || iter_count > max_iter) {
      // found new maximum
      f_best_highs[my_index] = fmax(f_best_highs[my_index], f.upper());
    } else {
      iter_count++;
      vector<box_t> X_12 = split_box(X);
      for(auto Xi : X_12) {
	interval<double> e = F(midpoint(Xi));
	if(e.lower() > f_best_low) {
	  f_best_low = e.lower();
	}
	  Qs[my_index].push(Xi);
      }
    }
  }
}
