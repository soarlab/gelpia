#include "harness.h"

double serial_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter, 
		     const std::function<boost::numeric::interval<double>(const box_t &)> & F);

double par1_solver(const box_t & X_0, double x_tol, double f_tol, int max_iter, 
		   const std::function<boost::numeric::interval<double>(const box_t &)> & F);
