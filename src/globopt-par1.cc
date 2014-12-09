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

using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/* Number of threads */
int num_threads = 2;

/* Global queue */
std::queue<box_t> Q;
/* Global queue guard */
std::mutex Q_l;

std::atomic<double> f_best_low;
std::atomic<double> f_best_high;
std::atomic<int> iter_count;
std::atomic<int> current_working;

/*
 * Divides given interval box along longest dimension
 * Arguments:
 *          X - given box
 * Return: vector of two new boxes
 */
vector<box_t> split_box(const box_t & X);




/*
 * Finds midpoint of given box
 * Arguments:
 *          X - given box
 * Return: box whose dimentions align to the single midpoint
 */
box_t midpoint(const box_t & X);




/*
 * Caluclates the width of the box, the length of the longest dimension
 * Arguments:
 *          X - given box
 * Return: width scalar
 */
double width(const box_t & X);

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
	return;
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
