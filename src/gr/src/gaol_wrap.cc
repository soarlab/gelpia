#include <iostream>
#include <string>
#include "gaol/gaol.h"
#include "gaol_wrap.hh"
#include <cmath>
#include <cstring>
#include <cassert>
#include <cfenv>
#define TO_INTERVAL(x) (*(reinterpret_cast<interval*>(x)))
#define TO_INTERVAL_C(x) (*(reinterpret_cast<const interval*>(x)))
#define TO_STACK(x) (*(reinterpret_cast<gaol_int*>(x)))

// The following assertions ensure that the punned type gaol_int is correct.
static_assert(sizeof(interval) == sizeof(gaol_int), 
	      "Size of punned type gaol_int does not match size of interval.");
static_assert(alignof(interval) == alignof(gaol_int),
	      "Alignment of punned type gaol_int does not match alignment of interval.");

static_assert(true == 1 && false == 0,
	      "true is not 1 or false is not 0");

void make_interval_dd(double inf, double sup, gaol_int* out) {
    TO_INTERVAL(out) = interval(inf, sup);
}

void make_interval_d(double p, gaol_int* out) {
  TO_INTERVAL(out) = interval(p);
}

// These Gaol functions my throw. Exceptions must be caught here since Rust
// has no mechanism for handling these.

void make_interval_ss(const char* inf, const char* sup, gaol_int* out, char* success) {
  try {
    TO_INTERVAL(out) = interval(inf, sup);
    *success = 1;
  }
  catch(...) {
    *success = 0;
  }
}

void make_interval_s(const char* in, gaol_int* out, char* success) {
  try {
    TO_INTERVAL(out) = interval(in);
    *success = 1;
  }
  catch(...) {
    *success = 0;
  }
}

void make_interval_i(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = interval(TO_INTERVAL_C(in));
}

gaol_int make_interval_e() {
  interval result;
  return TO_STACK(&result);
}
//  void del_int(gaol_int); 
  
void add(const gaol_int* a, const gaol_int* b, gaol_int* out) {
  TO_INTERVAL(out) = TO_INTERVAL_C(a) + TO_INTERVAL_C(b);
}

void iadd(gaol_int* a, const gaol_int* b) {
  TO_INTERVAL(a) += TO_INTERVAL_C(b);
}

void sub(const gaol_int* a, const gaol_int* b, gaol_int* out) {
  TO_INTERVAL(out) = TO_INTERVAL_C(a) - TO_INTERVAL_C(b);
}

void isub(gaol_int* a, const gaol_int* b) {
  TO_INTERVAL(a) -= TO_INTERVAL_C(b);
}

void mul(const gaol_int* a, const gaol_int* b, gaol_int* out) {
  TO_INTERVAL(out) = TO_INTERVAL_C(a) * TO_INTERVAL_C(b);
}

void imul(gaol_int* a, const gaol_int* b) {
  TO_INTERVAL(a) *= TO_INTERVAL_C(b);
}

void div_g(const gaol_int* a, const gaol_int* b, gaol_int* out) {
  TO_INTERVAL(out) = TO_INTERVAL_C(a) / TO_INTERVAL_C(b);
}

void idiv_g(gaol_int* a, const gaol_int* b) {
  TO_INTERVAL(a) /= TO_INTERVAL_C(b);
}

void neg_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = -TO_INTERVAL_C(in);
}

void ineg_g(gaol_int* x) {
  TO_INTERVAL(x) = -TO_INTERVAL(x);
}

void sin_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = sin(TO_INTERVAL_C(in));
}

void asin_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = asin(TO_INTERVAL_C(in));
}

void isin_g(gaol_int* x) {
  TO_INTERVAL(x) = sin(TO_INTERVAL(x));
}

void iasin_g(gaol_int* x) {
  TO_INTERVAL(x) = asin(TO_INTERVAL(x));
}

void sqrt_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = sqrt(TO_INTERVAL_C(in));
}

void isqrt_g(gaol_int* x) {
  TO_INTERVAL(x) = sqrt(TO_INTERVAL(x));
}

void cos_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = cos(TO_INTERVAL_C(in));
}

void icos_g(gaol_int* x) {
  TO_INTERVAL(x) = cos(TO_INTERVAL(x));
}

void acos_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = acos(TO_INTERVAL_C(in));
}

void iacos_g(gaol_int* x) {
  TO_INTERVAL(x) = acos(TO_INTERVAL(x));
}

void tan_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = tan(TO_INTERVAL_C(in));
}

void itan_g(gaol_int* x) {
  TO_INTERVAL(x) = tan(TO_INTERVAL(x));
}

void atan_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = atan(TO_INTERVAL_C(in));
}

void iatan_g(gaol_int* x) {
  TO_INTERVAL(x) = atan(TO_INTERVAL(x));
}

// Hyperbolic functions
void sinh_g(const gaol_int* in, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(out) = (exp(x) - exp(-x))/2.0;
}

void isinh_g(gaol_int* in) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(in) = (exp(x) - exp(-x))/2.0;
}

void asinh_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = asinh(TO_INTERVAL_C(in));
}

void iasinh_g(gaol_int* x) {
  TO_INTERVAL(x) = asinh(TO_INTERVAL(x));
}

void cosh_g(const gaol_int* in, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(out) = (exp(x)+exp(-x))/2.0;
}

void icosh_g(gaol_int* in) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(in) = (exp(x)+exp(-x))/2.0;
}

void acosh_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = acosh(TO_INTERVAL_C(in));
}

void iacosh_g(gaol_int* x) {
  TO_INTERVAL(x) = acosh(TO_INTERVAL(x));
}

void tanh_g(const gaol_int* in, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(out) = (exp(2.0*x) - 1)/(exp(2.0*x) + 1.0);
}

void itanh_g(gaol_int* in) {
  const interval& x = TO_INTERVAL_C(in);
  TO_INTERVAL(in) = (exp(2.0*x) - 1)/(exp(2.0*x) + 1.0);
}

void atanh_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = atanh(TO_INTERVAL_C(in));
}

void iatanh_g(gaol_int* x) {
  TO_INTERVAL(x) = atanh(TO_INTERVAL(x));
}

//
static double
fp2(double f) {
  auto fc = std::fpclassify(f);
  if(fc == FP_ZERO ||
     fc == FP_INFINITE ||
     fc == FP_NAN) {
    return f;
  }
  if (f < 0) {
    return -fp2(-f);
  }
  int exp;
  double x = std::frexp(f, &exp);
  if (x == 0.5) {
    return std::ldexp(1.0, exp-2);
  }
  else {
    return std::ldexp(1.0, exp-1);
  }
}

void fp2_g(const gaol_int* a, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(a);
  TO_INTERVAL(out) = interval(fp2(x.left()), fp2(x.right()));
}

void ifp2_g(gaol_int* a) {
  interval& x = TO_INTERVAL(a);
  x = interval(fp2(x.left()), fp2(x.right()));
}

void symint_g(const gaol_int* a, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(a);
  double m = x.mag();
  TO_INTERVAL(out) = interval(-m, m);
}

void isymint_g(gaol_int* a) {
  interval& x = TO_INTERVAL(a);
  double m = x.mag();
  x = interval(-m, m);
}

//
void exp_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = exp(TO_INTERVAL_C(in));
}

void iexp_g(gaol_int* x) {
  TO_INTERVAL(x) = exp(TO_INTERVAL(x));
}

void log_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = log(TO_INTERVAL_C(in));
}

void ilog_g(gaol_int* x) {
  TO_INTERVAL(x) = log(TO_INTERVAL(x));
}

void abs_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = abs(TO_INTERVAL_C(in));
}

void iabs_g(gaol_int* x) {
  TO_INTERVAL(x) = abs(TO_INTERVAL(x));
}

static interval
dabs(const interval& x) {
  interval sx = sqr(x);
  return 4*x*(15 + 1024*sx*(-5 + 576*sx));
}

void dabs_g(const gaol_int* in, gaol_int* out) {
  const interval& x = TO_INTERVAL_C(in);
  interval& result = TO_INTERVAL(out);
  const double v = 1/16.0;
  if (x.right() < -v) {
    result = -1;
  }
  else if (x.left() > v) {
    result = 1;
  }
  else if (x.left() < -v && x.right() > v) {
    result = interval(-1, 1);
  }
  else if (x.left() < -v && x.right() <= v) {
    interval i = dabs(x.right());
    result = interval(-1.0, std::max(-1.0, i.right()));
  }
  else if (x.left() >= v && x.right() > v) {
    interval i = dabs(x.left());
    result = interval(std::min(1.0, i.left()), 1.0);
  }
  else {
    result = dabs(x);
  }
}

void idabs_g(gaol_int* in) {
  interval& x = TO_INTERVAL(in);
  interval& result = TO_INTERVAL(in);
  const double v = 1/16.0;
  if (x.right() < -v) {
    result = -1;
  }
  else if (x.left() > v) {
    result = 1;
  }
  else if (x.left() < -v && x.right() > v) {
    result = interval(-1, 1);
  }
  else if (x.left() < -v && x.right() <= v) {
    interval i = dabs(x.right());
    result = interval(-1.0, std::max(-1.0, i.right()));
  }
  else if (x.left() >= v && x.right() > v) {
    interval i = dabs(x.left());
    result = interval(std::min(1.0, i.left()), 1.0);
  }
  else {
    result = dabs(x);
  }

}


void pow_ig(const gaol_int* a, int b, gaol_int* out) {
  TO_INTERVAL(out) = pow(TO_INTERVAL_C(a), b);
}

void ipow_ig(gaol_int* a, int b) {
  TO_INTERVAL(a) = pow(TO_INTERVAL(a), b);
}
  
void pow_vg(const gaol_int* a, const gaol_int* b, gaol_int* out) {
  TO_INTERVAL(out) = pow(TO_INTERVAL_C(a), TO_INTERVAL_C(b));
}

void ipow_vg(gaol_int* a, const gaol_int* b) {
  TO_INTERVAL(a) = pow(TO_INTERVAL(a), TO_INTERVAL_C(b));
}

void print(gaol_int* x) {
  std::cout << TO_INTERVAL(x) << std::endl;
}


const char* to_str(const gaol_int* x) {
  //  interval::precision(100);
  std::string t(TO_INTERVAL_C(x));
  char* result = reinterpret_cast<char*>(malloc((t.size() + 1) * sizeof(char)));
  strcpy(result, t.c_str());
  return result;
}

double upper_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).right();
}

double lower_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).left();
}

double width_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).width();
}

gaol_int midpoint_g(const gaol_int* x) {
  interval result = TO_INTERVAL_C(x).midpoint();
  return TO_STACK(&result);
}

void split_g(const gaol_int* in, gaol_int* out_1, gaol_int* out_2) {
  TO_INTERVAL_C(in).split(TO_INTERVAL(out_1), TO_INTERVAL(out_2));
}

char is_empty_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).is_empty();
}

char straddles_zero_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).straddles_zero();
}
char is_canonoical_g(const gaol_int* x) {
  return TO_INTERVAL_C(x).is_canonical();
}
