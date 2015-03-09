
#ifndef INTERVAL_H
#define INTERVAL_H

#include <boost/numeric/interval.hpp>
#include <boost/multiprecision/gmp.hpp> 

typedef mp::number<mp::mpfr_float_backend<300> > my_float;

class interval {
  boost::numeric::interval<my_float> my_interval;
  
 public:
  interval(const std::string &low, const std::string &high);
  interval(const interval &in);
  interval(interval &&in);
  interval &operator=(const interval &in);
  interval &operator=(interval &&in);

  my_float upper() const;
  my_float lower() const;
  
  ~interval();
}

#endif
