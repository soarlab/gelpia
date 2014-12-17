#include "harness.h"
#include <boost/numeric/interval/rounded_transc.hpp>
#include <cmath>

using boost::numeric::interval;
using std::vector;
using boost::numeric::interval_lib::rounded_transc_exact;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::policies;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::checking_strict;

/*
* Testing interval function
*/
interval<double> F0(const box_t & X)
{
    assert(X.size()==2);
  return -(pow(X[0],2)*12.0 
    - pow(X[0],4)*6.3
    + pow(X[0],6) 
    + X[0]*X[1]*3.0
    - pow(X[1],2)*12.0
    + pow(X[1],4)*12.0);

}

boost::numeric::interval<double> F0_p(const interval_t* X, size_t size)
{
  assert(size==2);
  return -(pow(X[0],2)*12.0 
    - pow(X[0],4)*6.3
    + pow(X[0],6) 
    + X[0]*X[1]*3.0
    - pow(X[1],2)*12.0
    + pow(X[1],4)*12.0);

}
boost::numeric::interval<double> F1_p(const interval_t* X, size_t size)
{
  assert(size == 2);
  interval<double> one(1.0,1.0);
  interval<double> result = X[0] * (one-X[0]) * (one-X[1]);
  return result;
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

interval<double> F2(const box_t & X)
{
  assert(X.size() == 2);
  return pow(X[0],4) + pow(X[1], 4)
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0;
}


interval<double> F3(const box_t & X)
{
  assert(X.size() == 2);
  return pow(X[0],4) + pow(X[1], 4)
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0;
}
interval<double> F4(const box_t & X)
{
  assert(X.size() == 2);
  return pow(X[0],4) + pow(X[1], 4)
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0
    - X[0]*3.0 - X[1]*3.0
    + X[0]*3.0 + X[1]*3.0;

}

/* 
 * Problems from Alexey's opt_problems text file 
 */

interval_t delta_x(const box_t & X)
{
  assert(X.size() == 6);
  const interval_t& x1 = X[0], &x2 = X[1], &x3 = X[2], &x4 = X[3], &x5 = X[4], &x6 = X[5];
  return x1*x4*(-x1 + x2 + x3 - x4 + x5 + x6) +
    x2*x5*(x1 - x2 + x3 + x4 -x5 + x6) +
    x3*x6*(x1 + x2 - x3 + x4 + x5 - x6)
    -x2*x3*x4 - x1*x3*x5 - x1*x2*x6 -x4*x5*x6;
}
interval_t delta_y(const box_t & Y)
{
  assert(Y.size() == 6);
  const interval_t& y1 = Y[0], &y2 = Y[1], &y3 = Y[2], &y4 = Y[3], &y5 = Y[4], &y6 = Y[5];
  return delta_x({y1*y1, y2*y2, y3*y3, y4*y4, y5*y5, y6*y6});
}

interval_t delta_x4(const box_t & X)
{
  assert(X.size() == 6);
  const interval_t& x1 = X[0], &x2 = X[1], &x3 = X[2], &x4 = X[3], &x5 = X[4], &x6 = X[5];
  return -x2 * x3 - x1 * x4 + x2 * x5 +
    x3 * x6 - x5 * x6 + x1 * (-x1 + x2 + x3 - x4 + x5 + x6);
}

interval_t rho_x(const box_t & X)
{
  assert(X.size() == 6);
  const interval_t& x1 = X[0], &x2 = X[1], &x3 = X[2], &x4 = X[3], &x5 = X[4], &x6 = X[5];
  interval_t two = interval_t(2);
  return -x1*x1*x4*x4 - x2*x2*x5*x5 - x3*x3*x6*x6 +
    two*x1*x2*x4*x5 + two*x1*x3*x4*x6 + two*x2*x3*x5*x6;
}

interval_t rad2_x(const box_t& X)
{
  assert(X.size() == 6);
  return rho_x(X) / (interval_t(4) * delta_x(X));
}

interval_t atn2(const box_t& X)
{
  assert(X.size() == 2);
  // Hack to get atan to work: http://www.wilmott.com/messageview.cfm?catid=44&threadid=87321&STARTPAGE=3&FTVAR_MSGDBTABLE=
  interval<double, policies<rounded_transc_exact<double,rounded_math<double>> , checking_strict<double>>> x(X[0].lower(), X[0].upper());
  interval<double, policies<rounded_transc_exact<double,rounded_math<double>> , checking_strict<double>>> y(X[1].lower(), X[1].upper());
  
  auto inter = atan(y/x);
  return interval_t(inter.lower(), inter.upper());
}

interval_t dih_x(const box_t& X)
{
  assert(X.size() == 6);
  const interval_t& x1 = X[0], &x2 = X[1], &x3 = X[2], &x4 = X[3], &x5 = X[4], &x6 = X[5];
  interval_t d_x4 = delta_x4(X);
  interval_t d = delta_x(X);
  
  return boost::numeric::interval_lib::pi<interval_t>()/interval_t(2) + atn2({sqrt(interval_t(4)*x1*d), -d_x4});
}

interval_t dih_y(const box_t& Y)
{
  assert(Y.size() == 6);
  const interval_t& y1 = Y[0], &y2 = Y[1], &y3 = Y[2], &y4 = Y[3], &y5 = Y[4], &y6 = Y[5];
  return dih_x({y1*y1, y2*y2, y3*y3, y4*y4, y5*y5, y6*y6});
}

interval_t opt1(const box_t& Y)
{
  assert(Y.size() == 6);
  return -delta_y(Y);
}

box_t opt1_int(6,interval_t(2, 2.52));

interval_t opt2(const box_t& X)
{
  assert(X.size() == 6);
  return interval_t(2) - rad2_x(X);
}

box_t opt2_int{interval_t(2*2*1.3254*1.3254, 8), interval_t(2*2*1.3254*1.3254, 8),
    interval_t(4, 8), interval_t(4, 8), interval_t(4, 8), interval_t(4, 8)};

interval_t opt3(const box_t& Y)
{
  assert(Y.size() == 6);
  const interval_t& y1 = Y[0], &y2 = Y[1], &y3 = Y[2], &y4 = Y[3], &y5 = Y[4], &y6 = Y[5];
  return -(dih_y(Y) - 1.629 +
	   (0.414*(y2 + y3 + y5 + y6 -8.0)) -
	   (0.763*(y4 - 2.52)) -
	   (0.3 * (y1 - 2.0)));
}

box_t opt3_int{interval_t(2, 2.52), interval_t(2, 2.52), interval_t(2, 2.52),
    interval_t(2.52, std::sqrt(8.0)), interval_t(2, 2.52), interval_t(2, 2.52)};
