#include <assert.h>
#include "interval.h"


interval::interval(const std::string &low_string, const std::string &high_string) {
  large_float_t low, high;
  low = static_cast<large_float_t>(low_string);
  high = static_cast<large_float_t>(high_string);
  assert(low <= high);
  value = interval_t(low, high);
}
  
interval::interval(const interval &in) {
  value = interval_t(static_cast<large_float_t>(in.value.lower()),
		     static_cast<large_float_t>(in.value.upper()));
}

interval::interval(const interval_t &in) {
  value = in;
}  

bool interval::operator==(const interval &c) const {
  return (c.lower() == this->lower()) && (c.upper() == this->upper());
}

bool interval::operator!=(const interval &c) const {
  return !(*this == c);
}

large_float interval::width() {
  return large_float(value.upper() - value.lower());
}

large_float interval::lower() const {
  return static_cast<large_float>(this->value.lower());
}

large_float interval::upper() const {
  return static_cast<large_float>(this->value.upper());
}
  
std::string& interval::to_string() {
  str_rep = "[";
  str_rep += boost::lexical_cast<std::string>(value.lower());
  str_rep += ", ";
  str_rep += boost::lexical_cast<std::string>(value.upper());
  str_rep += "]";
  return str_rep;
}

interval_t interval::get_value() const { 
  return value; 
}

interval::~interval() {;}
