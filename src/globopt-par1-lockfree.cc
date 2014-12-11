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
#include <boost/lockfree/queue.hpp>
#include "helpers.h"

using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/* Number of threads */
int num_threads = 2;

/* Global queue */
boost::lockfree::queue<interval_t*, boost::lockfree::capacity<10000>> Q;
/* Global queue guard */

std::atomic<double> f_best_low;
std::atomic<double> f_best_high;
std::atomic<int> iter_count;
std::atomic<int> current_working;


void par1_lockfree_worker(double x_tol, double f_tol, int max_iter, size_t,
			  const function<interval<double>(const interval_t*, size_t)> & F);

double par1_lockfree_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter,
			    const function<interval<double>(const interval_t*, size_t)> & F)
{
  f_best_low = -INFINITY;
  f_best_high = -INFINITY;
  iter_count = 0;
  current_working = 0;

  // Initialize queue
  interval_t* X_0_p = new interval_t[X_0.size()];
  for(size_t i = 0; i < X_0.size(); ++i) {
    X_0_p[i] = X_0[i];
  }
  Q.push(X_0_p);

  size_t size = X_0.size();
  // Create threads
  std::vector<std::thread> threads;
  for(int i = 0; i < num_threads; ++i) {
    threads.push_back(
		      std::thread(
				  par1_lockfree_worker,
				  x_tol,
				  f_tol,
				  max_iter,
				  size,
				  std::ref(F)));
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
void par1_lockfree_worker(double x_tol, double f_tol, int max_iter, size_t size,
			  const function<interval<double>(const interval_t*, size_t)> & F)
{
  while(true) {
    // grab new work item
    interval_t* X;
    {
      //      std::lock_guard<std::mutex> m{Q_l};
      if(Q.empty()) {
	if(!current_working.load()) {
	  return;
	}
	else {
	  continue;
	}
      }

      if(!Q.pop(X))
	continue;
      current_working++;
    }

    interval<double> f = F(X, size);
    double w = width(X, size);
    double fw = width(f);

    if(f.upper() < f_best_low
       || w <= x_tol
       || fw <= f_tol
       || iter_count > max_iter) {
      // found new maximum
      f_best_high = fmax(f_best_high.load(), f.upper());
    } else {
      iter_count++;
      vector<interval_t*> X_12 = split_box(X,size);
      for(auto Xi : X_12) {
	interval<double> e = F(midpoint(Xi,size), size);
	if(e.lower() > f_best_low) {
	  f_best_low = e.lower();
	}
	{
	  // std::lock_guard<std::mutex> lock{Q_l};
	  Q.push(Xi);
	}
      }
    }
    delete[] X;
    current_working--;
  }
}
