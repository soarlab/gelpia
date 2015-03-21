
#ifndef INTERVAL_H
#define INTERVAL_H

#include "large_float.h" 
#include <boost/numeric/interval.hpp>
#include <boost/lexical_cast.hpp>
#include <string>

typedef boost::numeric::interval<large_float_t> interval_t;


class interval {
  interval_t value;
  std::string str_rep;
 public:
  interval(const std::string &low_string, const std::string &high_string) {
    value = interval_t(static_cast<large_float_t>(low_string),
		       static_cast<large_float_t>(high_string));
  }
  
  interval(const interval &in) {
    value = interval_t(static_cast<large_float_t>(in.value.lower()),
		       static_cast<large_float_t>(in.value.upper()));
  }

  interval(const interval_t &in) {
    value = in;
  }
  
  large_float width() {
    return large_float(value.upper() - value.lower());
  }

  large_float lower() const {return static_cast<large_float>(this->value.lower()); }
  large_float upper() const {return static_cast<large_float>(this->value.upper()); }
  
  std::string& to_string() {
    if(str_rep == "") {
      str_rep += "[";
      str_rep += boost::lexical_cast<std::string>(value.lower());
      str_rep += ", ";
      str_rep += boost::lexical_cast<std::string>(value.upper());
      str_rep += "]";
    }
    return str_rep;
  }

  interval_t get_value() const { return value; }
  ~interval(){;}
};

#endif
