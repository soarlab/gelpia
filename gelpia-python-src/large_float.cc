#include "large_float.h"

// Instantiate the template
template large_float_t;
large_float::large_float(const std::string &number) {
  value = static_cast<large_float_t>(number);
}

large_float::large_float(const large_float &in) {
  value = static_cast<large_float_t>(in.value);
}

large_float::large_float(const large_float_t &in) {
  value = in;
}

bool large_float::operator<  (const large_float &c) const { return (this->value <  c.value); }
bool large_float::operator== (const large_float &c) const { return (this->value == c.value); }
bool large_float::operator<= (const large_float &c) const { return (this->value <= c.value); }
bool large_float::operator>  (const large_float &c) const { return (this->value >  c.value); }
bool large_float::operator>= (const large_float &c) const { return (this->value >= c.value); }
bool large_float::operator!= (const large_float &c) const { return (this->value != c.value); }

large_float_t large_float::get_value() const{
  return value;
}

large_float large_float::operator- () {
  large_float result;
  result.value = this->value*-1;
  return result;
}

std::string &large_float::to_string() {
  // Lazy initialization of the internal string
  if(str_rep == "")
    str_rep = value.str();
  return str_rep;
}

// Needed for SWIG
large_float::~large_float() {;}
