#ifndef REWRITE_H
#define REWRITE_H

#include <dlfcn.h>
#include <boost/numeric/interval.hpp>
#include <vector>
#include <boost/numeric/interval/rounded_transc.hpp>
#include <functional>
#include <iostream>
#include <cerrno>
#include <cstring>
#include <iostream>

using boost::numeric::interval;
using std::vector;
using boost::numeric::interval_lib::rounded_transc_exact;
using boost::numeric::interval_lib::policies;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::checking_strict;
typedef interval<double> box;
typedef vector<interval<double>> box_t;
typedef box gelpia_function_t(const box_t &);

class gelpia_func {
  gelpia_function_t *func;
  void *handle;

public:
  gelpia_func(const std::string &function_name);
  gelpia_function_t *get_function();
  ~gelpia_func();
};

#endif
