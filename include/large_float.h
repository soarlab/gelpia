
#ifndef LARGE_FLOAT_H
#define LARGE_FLOAT_H

#include <boost/multiprecision/mpfr.hpp>

typedef boost::multiprecision::number<boost::multiprecision::mpfr_float_backend<300>>  large_float_t;

class large_float {
  large_float_t value;
  
 public:
  large_float(const std::string &number) {
    value = static_cast<large_float_t>(number);
  }
  
  large_float(const large_float &in) {
    value = static_cast<large_float_t>(in.value);
  }
  
  large_float(large_float_t in) {
    value = in;
  }

  bool operator< (const large_float &c) const {
    return (this->value < c.value);
  }

  bool operator== (const large_float &c)const {
    return (this->value == c.value);
  }

  std::string to_string() { return this->value.str(); }
  
  ~large_float(){;}
};

#endif
