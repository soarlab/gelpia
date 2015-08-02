#include <iostream>
#include <string>
#include "gaol/gaol.h"
#include "gaol_wrap.hh"
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

void make_interval_dd(double inf, double sup, gaol_int* out) {
  TO_INTERVAL(out) = interval(inf, sup);
}

void make_interval_ss(const char* inf, const char* sup, gaol_int* out) {
  TO_INTERVAL(out) = interval(inf, sup);
}

void make_interval_s(const char* in, gaol_int* out) {
  TO_INTERVAL(out) = interval(in);
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

void isin_g(gaol_int* x) {
  TO_INTERVAL(x) = sin(TO_INTERVAL(x));
}

void cos_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = cos(TO_INTERVAL_C(in));
}

void icos_g(gaol_int* x) {
  TO_INTERVAL(x) = cos(TO_INTERVAL(x));
}

void tan_g(const gaol_int* in, gaol_int* out) {
  TO_INTERVAL(out) = tan(TO_INTERVAL_C(in));
}

void itan_g(gaol_int* x) {
  TO_INTERVAL(x) = tan(TO_INTERVAL(x));
}

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
