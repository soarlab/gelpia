#include "harness.h"

using boost::numeric::interval;

typedef interval<double> interval_t;

boost::numeric::interval<double> F0(const box_t & X);
boost::numeric::interval<double> F1(const box_t & X);
boost::numeric::interval<double> F2(const box_t & X);
boost::numeric::interval<double> F3(const box_t & X);
boost::numeric::interval<double> F4(const box_t & X);

interval_t delta_x(const box_t & X);
interval_t delta_y(const box_t & X);
interval_t delta_x4(const box_t & X);
interval_t rho_x(const box_t & X);
interval_t rad2_x(const box_t& X);
interval_t atn(const box_t& X);
interval_t dih_x(const box_t& X);
interval_t dih_y(const box_t& X);

interval_t opt1(const box_t& X);
interval_t opt2(const box_t& X);
interval_t opt3(const box_t& X);

boost::numeric::interval<double> F0_p(const interval_t* X, size_t size);
boost::numeric::interval<double> F1_p(const interval_t* X, size_t size);

extern box_t opt1_int;
extern box_t opt2_int;
extern box_t opt3_int;
