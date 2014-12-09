#include <boost/numeric/interval.hpp>
#include <vector>
#include <queue>
#include <cmath>
#include <iostream>
#include <functional>
#include <cassert>

using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/*
* Divides given interval box along longest dimension
* Arguments:
*          X - given box
* Return: vector of two new boxes
*/
vector<box_t> split_box(const box_t & X)
{
// Split the box along longest dimension
  double longest = 0.0;
  int longest_idx = 0;
  for(uint i = 0; i < X.size(); ++i) {
    if(width(X[i]) > longest) {
      longest = width(X[i]);
      longest_idx = i;
    }
  }

// create two copies
  box_t X1(X);
  box_t X2(X);

// split boxes along longest dimension
  double m = median(X[longest_idx]);
  X1[longest_idx].assign(X1[longest_idx].lower(), m);
  X2[longest_idx].assign(m, X2[longest_idx].upper());

  return vector<box_t>{X1, X2};
}




/*
* Finds midpoint of given box
* Arguments:
*          X - given box
* Return: box whose dimentions align to the single midpoint
*/
box_t midpoint(const box_t & X)
{
  box_t result(X.size());

  for(uint i = 0; i < X.size(); ++i) {
    double m = median(X[i]);
    result[i].assign(m,m);
  }

  return result;
}




/*
* Caluclates the width of the box, the length of the longest dimension
* Arguments:
*          X - given box
* Return: width scalar
*/
double width(const box_t & X)
{
  double longest = 0.0;
  for(uint i = 0; i < X.size(); ++i) {
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
double serial_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter,
  const function<interval<double>(const box_t &)> & F)
{
  std::queue<box_t> Q;
  Q.push(X_0);

  double f_best_low = -INFINITY, f_best_high = -INFINITY;
  int iter_count = 0;

  while(!Q.empty()) {
// grab new work item
    box_t X = Q.front();
    Q.pop();


    interval<double> f = F(X);
    double w = width(X);
    double fw = width(f);

    if(f.upper() < f_best_low
      || w <= x_tol
      || fw <= f_tol
      || iter_count > max_iter) {
// found new maximum
      f_best_high = fmax(f_best_high, f.upper());
    continue;
  } else {
    iter_count++;
    vector<box_t> X_12 = split_box(X);
    for(auto Xi : X_12) {
      interval<double> e = F(midpoint(Xi));
      if(e.lower() > f_best_low) {
        f_best_low = e.lower();
      }
      Q.push(Xi);
    }
  }
}
return f_best_high;
}
