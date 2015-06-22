#include <assert.h>
#include "fast_interval.h"


fast_interval::fast_interval(const std::string &low_string, const std::string &high_string) {
  double_t low, high;
  low = strtod(low_string.c_str(), NULL);
  high = strtod(high_string.c_str(), NULL);
  assert(low <= high);
  value = fast_interval_t(low, high);
}
 
fast_interval::fast_interval(const double &low, const double &high) {
  assert(low <= high);
  value = fast_interval_t(low, high);
} 

fast_interval::fast_interval(const fast_interval &in) {
  value = fast_interval_t(in.value.inf(),
			  in.value.sup());
}

fast_interval::fast_interval(const fast_interval_t &in) {
  value = in;
}  

bool fast_interval::operator==(const fast_interval &c) const {
  return c.value.seq(this->value);
}

bool fast_interval::operator!=(const fast_interval &c) const {
  return c.value.sne(this->value);
}

double fast_interval::width() const {
  return this->value.diam();
}

double fast_interval::lower() const {
  return this->value.inf();
}

double fast_interval::upper() const {
  return this->value.sup();
}
  
std::string& fast_interval::to_string() const {
  if(str_rep == "") {
    std::stringstream ss;
    ss << std::setprecision(17);
    ss << "[";
    ss << value.sup();
    ss << ", ";
    ss << value.inf();
    ss <<  "]";
    str_rep = ss.str();
  }
  return str_rep;
}

fast_interval_t fast_interval::get_value() const { 
  return value; 
}


fast_interval p2(const fast_interval & x)
{
  return x;
}
// Needed for SWIG
fast_interval::~fast_interval() {;}
