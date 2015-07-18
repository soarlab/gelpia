#ifndef TEST_H
#define TEST_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct gaol_int {void* data;} gaol_int;

  gaol_int make_interval_dd(double, double);
  gaol_int make_interval_ss(const char*, const char*);
  gaol_int make_interval_s(const char*);
  gaol_int make_interval_i(gaol_int);
  gaol_int make_interval_e();
  void del_int(gaol_int); 
  
  gaol_int add(gaol_int, gaol_int);
  gaol_int iadd(gaol_int, gaol_int);
  gaol_int sub(gaol_int, gaol_int);
  gaol_int isub(gaol_int, gaol_int);
  gaol_int mul(gaol_int, gaol_int);
  gaol_int imul(gaol_int, gaol_int);
  gaol_int div_g(gaol_int, gaol_int);
  gaol_int idiv_g(gaol_int, gaol_int);
  gaol_int neg_g(gaol_int);
  gaol_int ineg_g(gaol_int);
  gaol_int sin_g(gaol_int);
  gaol_int isin_g(gaol_int);
  gaol_int cos_g(gaol_int);
  gaol_int icos_g(gaol_int);
  gaol_int tan_g(gaol_int);
  gaol_int itan_g(gaol_int);
  
  gaol_int exp_g(gaol_int);
  gaol_int iexp_g(gaol_int);
  
  gaol_int log_g(gaol_int);
  gaol_int ilog_g(gaol_int);

  gaol_int pow_ig(gaol_int, int);
  gaol_int ipow_ig(gaol_int, int);
  
  gaol_int pow_vg(gaol_int, gaol_int);
  gaol_int ipow_vg(gaol_int, gaol_int);
  
  void print(gaol_int);
  const char* to_str(gaol_int);

  double upper_g(gaol_int);
  double lower_g(gaol_int);
  double width_g(gaol_int);
  gaol_int midpoint_g(gaol_int);
  void split_g(gaol_int, gaol_int, gaol_int);

#ifdef __cplusplus
}
#endif
#endif
