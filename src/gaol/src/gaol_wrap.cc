#include <iostream>
#include <string>
#include "gaol/gaol.h"
#include "gaol_wrap.hh"
#include <cstring>

gaol_int make_interval_dd(double inf, double sup) {
  interval* x = new interval(inf, sup);
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int make_interval_ss(const char* inf, const char* sup) {
  interval* result = new interval(inf, sup);
  return (gaol_int){reinterpret_cast<void*>(result)};
}

gaol_int make_interval_s(const char* x) {
  interval* result = new interval(x); 
  return (gaol_int){reinterpret_cast<void*>(result)};
}

gaol_int make_interval_i(gaol_int x) {
  interval* result = new interval(*reinterpret_cast<interval*>(x.data));
  return (gaol_int) {reinterpret_cast<void*>(result)};
}

gaol_int make_interval_e() {
  interval* result = new interval();
  return (gaol_int) {reinterpret_cast<void*>(result)};
}

void del_int(gaol_int g) {
  delete reinterpret_cast<interval*>(g.data);
}

gaol_int add(gaol_int a, gaol_int b) {
  interval* x = new interval(*(reinterpret_cast<interval*>(a.data)) +
			     *(reinterpret_cast<interval*>(b.data)));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int iadd(gaol_int a, gaol_int b) {
  *reinterpret_cast<interval*>(a.data) += *reinterpret_cast<interval*>(b.data);
  return a;
}

gaol_int sub(gaol_int a, gaol_int b) {
  interval* x = new interval(*(reinterpret_cast<interval*>(a.data)) -
			     *(reinterpret_cast<interval*>(b.data)));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int isub(gaol_int a, gaol_int b) {
  *reinterpret_cast<interval*>(a.data) -= *reinterpret_cast<interval*>(b.data);
  return a;
}

gaol_int mul(gaol_int a, gaol_int b) {
  interval* x = new interval(*(reinterpret_cast<interval*>(a.data)) *
			     *(reinterpret_cast<interval*>(b.data)));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int imul(gaol_int a, gaol_int b) {
  interval* x = reinterpret_cast<interval*>(a.data);
  interval* y = reinterpret_cast<interval*>(b.data);
  *x *= *y;
  return a;
}

gaol_int div_g(gaol_int a, gaol_int b) {
  interval* x = new interval(*(reinterpret_cast<interval*>(a.data)) /
			     *(reinterpret_cast<interval*>(b.data)));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int idiv_g(gaol_int a, gaol_int b) {
  interval* x = reinterpret_cast<interval*>(a.data);
  interval* y = reinterpret_cast<interval*>(b.data);
  *x /= *y;
  return a;
}

gaol_int neg_g(gaol_int a) {
  interval* x = new interval(-(*(reinterpret_cast<interval*>(a.data))));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int ineg_g(gaol_int a) {
  interval* x = reinterpret_cast<interval*>(a.data);
  *x = -(*x);
  return a;
}

gaol_int sin_g(gaol_int a) {
  interval* x = new interval(sin(*(reinterpret_cast<interval*>(a.data))));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int isin_g(gaol_int a) {
  interval* x = reinterpret_cast<interval*>(a.data);
  *x = sin(*x);
  return a;
}

gaol_int cos_g(gaol_int a) {
  interval* x = new interval(cos(*(reinterpret_cast<interval*>(a.data))));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int icos_g(gaol_int a) {
  interval* x = reinterpret_cast<interval*>(a.data);
  *x = cos(*x);
  return a;
}

gaol_int tan_g(gaol_int a) {
  interval* x = new interval(tan(*(reinterpret_cast<interval*>(a.data))));
  return (gaol_int) {reinterpret_cast<void*>(x)};
}

gaol_int itan_g(gaol_int a) {
  interval* x = reinterpret_cast<interval*>(a.data);
  *x = tan(*x);
  return a;
}

gaol_int exp_g(gaol_int x) {
  interval* a = reinterpret_cast<interval*>(x.data);
  interval* result = new interval(exp(*a));
  return (gaol_int){reinterpret_cast<void*>(result)};
}

gaol_int iexp_g(gaol_int x) {
  interval* a = reinterpret_cast<interval*>(x.data);
  *a = exp(*a);
  return x;
}

gaol_int log_g(gaol_int x) {
  interval* a = reinterpret_cast<interval*>(x.data);
  interval* result = new interval(log(*a));
  return (gaol_int) {reinterpret_cast<void*>(result)};
}

gaol_int ilog_g(gaol_int x) {
  interval* a = reinterpret_cast<interval*>(x.data);
  *a = log(*a);
  return x;
}

gaol_int pow_ig(gaol_int x, int y) {
  interval* a = reinterpret_cast<interval*>(x.data);
  interval* result = new interval(pow(*a, y));
  return (gaol_int){reinterpret_cast<void*>(result)};
}

gaol_int ipow_ig(gaol_int x, int y) {
  interval* a = reinterpret_cast<interval*>(x.data);
  *a = pow(*a, y);
  return x;
}

gaol_int pow_vg(gaol_int x, gaol_int y) {
  interval* a = reinterpret_cast<interval*>(x.data);
  interval* b = reinterpret_cast<interval*>(y.data);
  interval* result = new interval(pow(*a, *b));
  return (gaol_int){reinterpret_cast<void*>(result)};
}
gaol_int ipow_vg(gaol_int x, gaol_int y) {
  interval* a = reinterpret_cast<interval*>(x.data);
  interval* b = reinterpret_cast<interval*>(y.data);
  *a = pow(*a, *b);
  return x;
}

void print(gaol_int x) {
  std::cout << *(reinterpret_cast<interval*>(x.data)) << std::endl;
}

const char* to_str(gaol_int x) {
  std::string t(*reinterpret_cast<interval*>(x.data));
  char* result = reinterpret_cast<char*>(malloc(t.size() * sizeof(char)));
  strcpy(result, t.c_str());
  return result;
}

double upper_g(gaol_int x) {
  return reinterpret_cast<interval*>(x.data)->right();
}

double lower_g(gaol_int x) {
  return reinterpret_cast<interval*>(x.data)->left();
}

double width_g(gaol_int x) {
  return reinterpret_cast<interval*>(x.data)->width();
}

gaol_int midpoint_g(gaol_int x) {
  interval* result = new interval(reinterpret_cast<interval*>(x.data)->mid());
  return (gaol_int) {reinterpret_cast<void*>(result)};
}

void split_g(gaol_int in, gaol_int out_1, gaol_int out_2) {
  interval* in_i = reinterpret_cast<interval*>(in.data);
  interval* out_1i = reinterpret_cast<interval*>(out_1.data);
  interval* out_2i = reinterpret_cast<interval*>(out_2.data);
  in_i->split(*out_1i, *out_2i);
}
