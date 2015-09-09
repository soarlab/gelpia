#ifndef TEST_H
#define TEST_H
#include <xmmintrin.h>

#ifdef __cplusplus
extern "C" {
#endif
  
  typedef struct gaol_int {__m128 data;} gaol_int;

  void make_interval_dd(double, double, gaol_int*);
  void make_interval_ss(const char*, const char*, gaol_int*);
  void make_interval_s(const char*, gaol_int*);
  void make_interval_i(gaol_int, gaol_int*);
  gaol_int make_interval_e();
  //  void del_int(gaol_int); 
  
  void add(const gaol_int*, const gaol_int*, gaol_int*);
  void iadd(gaol_int*, const gaol_int*);
  void sub(const gaol_int*, const gaol_int*, gaol_int*);
  void isub(gaol_int*, const gaol_int*);
  void mul(const gaol_int*, const gaol_int*, gaol_int*);
  void imul(gaol_int*, const gaol_int*);
  void div_g(const gaol_int*, const gaol_int*, gaol_int*);
  void idiv_g(gaol_int*, const gaol_int*);
  void neg_g(const gaol_int*, gaol_int*);
  void ineg_g(gaol_int*);
  void sin_g(const gaol_int*, gaol_int*);
  void isin_g(gaol_int*);
  void sqrt_g(const gaol_int*, gaol_int*);
  void isqrt_g(gaol_int*);
  void cos_g(const gaol_int*, gaol_int*);
  void icos_g(gaol_int*);
  void tan_g(const gaol_int*, gaol_int*);
  void itan_g(gaol_int*);
  
  void exp_g(const gaol_int*, gaol_int*);
  void iexp_g(gaol_int*);
  
  void log_g(const gaol_int*, gaol_int*);
  void ilog_g(gaol_int*);

  void pow_ig(const gaol_int*, int, gaol_int*);
  void ipow_ig(gaol_int*, int);

  void abs_g(const gaol_int*, gaol_int*);
  void iabs_g(gaol_int*);

  void pow_vg(const gaol_int*, const gaol_int*, gaol_int*);
  void ipow_vg(gaol_int*, const gaol_int*);
  
  void print(gaol_int*);
  const char* to_str(const gaol_int*);

  double upper_g(const gaol_int*);
  double lower_g(const gaol_int*);
  double width_g(const gaol_int*);
  gaol_int midpoint_g(const gaol_int*);
  void split_g(const gaol_int*, gaol_int*, gaol_int*);

#ifdef __cplusplus
}
#endif
#endif
