#include "harness.h"

boost::numeric::interval<double> F0(const box_t & X);
boost::numeric::interval<double> F1(const box_t & X);
boost::numeric::interval<double> F0_p(const interval_t* X, size_t size);
boost::numeric::interval<double> F1_p(const interval_t* X, size_t size);

