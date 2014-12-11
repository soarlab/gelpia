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
#include "helpers.h"

using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/* Number of threads */
extern int num_threads;

/* Global queue */
static std::queue<box_t> Q;
/* Global queue guard */
static std::mutex Q_l;

static std::atomic<double> f_best_low;
static std::atomic<double> f_best_high;
static std::atomic<int> iter_count;
static std::atomic<int> current_working;

void par1_worker(double x_tol, double f_tol, int max_iter,
		 const function<interval<double>(const box_t &)> & F);

double par1_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter,
		   const function<interval<double>(const box_t &)> & F)
{
  f_best_low = -INFINITY;
  f_best_high = -INFINITY;
  iter_count = 0;
  current_working = 0;

  // Initialize queue
  Q.push(X_0);
  // Create threads
  std::vector<std::thread> threads;
  for(int i = 0; i < num_threads; ++i) {
    threads.push_back(std::thread(par1_worker, x_tol, f_tol, max_iter, std::ref(F)));
  }
    
  // Wait
  for(auto & t : threads)
    t.join();
  // Return result
  return f_best_high;
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
void par1_worker(double x_tol, double f_tol, int max_iter,
		   const function<interval<double>(const box_t &)> & F)
{
  while(true) {
    // grab new work item
    box_t X;

    {
      std::lock_guard<std::mutex> m{Q_l};
      if(Q.empty()) {
	if(!current_working.load()) {
	  return;
	}
	else {
	  continue;
	}
      }

      X = Q.front();
      Q.pop();
      current_working++;
    }

    interval<double> f = F(X);
    double w = width(X);
    double fw = width(f);

    if(f.upper() < f_best_low
       || w <= x_tol
       || fw <= f_tol
       || iter_count > max_iter) {
      // found new maximum
      f_best_high = fmax(f_best_high.load(), f.upper());
    } else {
      iter_count++;
      vector<box_t> X_12 = split_box(X);
      for(auto Xi : X_12) {
	interval<double> e = F(midpoint(Xi));
	if(e.lower() > f_best_low) {
	  f_best_low = e.lower();
	}
	{
	  std::lock_guard<std::mutex> lock{Q_l};
	  Q.push(Xi);
	}
      }
    }
    current_working--;
  }
}
