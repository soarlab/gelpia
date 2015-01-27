
#ifndef OPTIMIZER_H
#define OPTIMIZER_H

#include <boost/numeric/interval.hpp>
#include <vector>
#include <functional>

typedef boost::numeric::interval<double> interval_t;
typedef std::vector<interval_t>  box_t;
typedef unsigned int uint;

typedef std::function<boost::numeric::interval<double>(box_t)> function_t;
typedef std::function<double (box_t, double, double, int, function_t)> solver_t;

struct answer {
  box_t input;
  double error;
};

#endif
