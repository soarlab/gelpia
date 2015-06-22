#include <assert.h>
#include "interval.h"

// Instantiate the interval template
template interval_t;

namespace bm = boost::multiprecision;


interval::interval(const std::string &low_string, const std::string &high_string) {
  large_float_t low, high;
  low = static_cast<large_float_t>(low_string);
  high = static_cast<large_float_t>(high_string);
  assert(low <= high);
  value = interval_t(low, high);
}
 
interval::interval(const large_float &low, const large_float &high) {
  value = interval_t(low.get_value(), high.get_value());
} 

interval::interval(const interval &in) {
  value = interval_t(bm::lower(in.value),
		     bm::upper(in.value));
}

interval::interval(const interval_t &in) {
  value = in;
}  

bool interval::operator==(const interval &c) const {
  return (bm::lower(c.value) == bm::lower(this->value)) && (bm::upper(c.value) == bm::upper(this->value));
}

bool interval::operator!=(const interval &c) const {
  return !(*this == c);
}

large_float interval::width() const {
  return large_float(bm::width(this->value));
}

large_float interval::lower() const {
  return large_float(bm::lower(this->value));
}

large_float interval::upper() const {
  return large_float(bm::upper(this->value));
}
  
std::string& interval::to_string() const {
  if(str_rep == "") {
    str_rep = "[";
    str_rep += boost::lexical_cast<std::string>(bm::lower(value));
    str_rep += ", ";
    str_rep += boost::lexical_cast<std::string>(bm::upper(value));
    str_rep += "]";
  }
  return str_rep;
}

interval_t interval::get_value() const { 
  return value; 
}


interval p2(const interval & x)
{
  return x;
}
// Needed for SWIG
interval::~interval() {;}
