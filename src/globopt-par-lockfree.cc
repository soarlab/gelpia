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

interval_t* midpoint_p(const interval_t* const X, size_t size);

/*
 * Divides given interval box along longest dimension
 * Arguments:
 *          X - given box
 * Return: vector of two new boxes
 */
vector<interval_t*> split_box_p(const interval_t* const X, size_t size)
{
  double longest = 0.0;
  int longest_idx = 0;
  // Split the box along longest dimension
  for(size_t i = 0; i < size; ++i) {
    if(width(X[i]) > longest) {
      longest = width(X[i]);
      longest_idx = i;
    }
  }

  // create two copies
  interval_t* X1 = new interval_t[size];
  interval_t* X2 = new interval_t[size];
  for(size_t i = 0; i < size; ++i) {
    X1[i] = X[i];
    X2[i] = X[i];
  }

  // split boxes along longest dimension
  double m = median(X[longest_idx]);

  X1[longest_idx].assign(X1[longest_idx].lower(), m);
  X2[longest_idx].assign(m, X2[longest_idx].upper());

  return vector<interval_t*>{X1, X2};
}


/*
 * Finds midpoint of given box
 * Arguments:
 *          X - given box
 * Return: box whose dimentions align to the single midpoint
 */
interval_t* midpoint_p(const interval_t* const X, size_t size)
{
  interval_t* result = new interval_t[size];
  for(size_t i = 0;i < size; ++i) {
    double m = median(X[i]);
    result[i].assign(m,m);
  }
  return result;
}

interval<double> F0_p(const interval_t* const X)
{
  return -(pow(X[0],2)*12.0 
    - pow(X[0],4)*6.3
    + pow(X[0],6) 
    + X[0]*X[1]*3.0
    - pow(X[1],2)*12.0
    + pow(X[1],4)*12.0);
}


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
  interval_t* X_0_p = new interval_t[X_0.size()];
  for(size_t i = 0; i < X_0.size(); ++i) {
    X_0_p[i] = X_0[i];
  }
  Q.push(X_0_p);
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

double width_p(const interval_t* const X, int size)
{
  double longest = 0.0;
  for(uint i = 0; i < size; ++i) {
    if(width(X[i]) > longest) {
      longest = width(X[i]);
    }
  }

  return longest;
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

    interval<double> f = F0_p(X);
    double w = width_p(X, 2);
    double fw = width(f);

    if(f.upper() < f_best_low
       || w <= x_tol
       || fw <= f_tol
       || iter_count > max_iter) {
      // found new maximum
      f_best_high = fmax(f_best_high.load(), f.upper());
    } else {
      iter_count++;
      vector<interval_t*> X_12 = split_box_p(X,2);
      for(auto Xi : X_12) {
	interval<double> e = F0_p(midpoint_p(Xi,2));
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
