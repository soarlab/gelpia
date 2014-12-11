#ifndef HARNESS_H
#define HARNESS_H
#include <boost/numeric/interval.hpp>
#include <functional>
#include <vector>

typedef boost::numeric::interval<double> interval_t;
typedef std::vector<interval_t>  box_t;

extern int num_threads;

double solve(const box_t & X_0,
	     double x_tol,
	     double f_tol,
	     int max_iter, 
	     const std::function<boost::numeric::interval<double>(const box_t &)> & F);
#endif
