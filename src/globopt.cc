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
  uint i;
  for(i = 0; i < X.size(); ++i) {
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
  X1[i].assign(X1[longest_idx].lower(), m);
  X2[i].assign(m, X2[longest_idx].upper());

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
* Testing interval function
*/
interval<double> F(const box_t & X)
{
  assert(X.size()==2);
  return -(pow(X[0],2)*12.0 
    - pow(X[0],4)*6.3
    + pow(X[0],6) 
    + X[0]*X[1]*3.0
    - pow(X[1],2)*12.0
    + pow(X[1],4)*12.0);
}




/*
* Testing interval function
*/
interval<double> F1(const box_t & X)
{
  assert(X.size() == 2);
  interval<double> one(1.0,1.0);
  interval<double> result = X[0] * (one-X[0]) * (one-X[1]);
  return result;
}




/*
* Testing interval function
*/
interval<double> F2(const box_t & X)
{
  assert(X.size() == 3);
  return X[0]*X[1] + X[1]*X[2] + X[0]*X[2];
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
double bb(const box_t & X_0, double x_tol, double f_tol, int max_iter, 
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

int main(int argc, char* argv[])
{
  box_t X_0{interval<double>(-5,5), interval<double>(-5,5),
    interval<double>(-5,5)};

    int iters = std::atoi(argv[1]);
    double f_best = bb(X_0, 0.0001, 0.0001, iters, F2);
    std::cout << f_best << std::endl;
  }
