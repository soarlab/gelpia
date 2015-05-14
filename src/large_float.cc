#include "large_float.h"


large_float::large_float(const std::string &number) {
  value = static_cast<large_float_t>(number);
}

large_float::large_float(const large_float &in) {
  value = static_cast<large_float_t>(in.value);
}

large_float::large_float(large_float_t in) {
  value = in;
}

bool large_float::operator<  (const large_float &c) const { return (this->value <  c.value); }
bool large_float::operator== (const large_float &c) const { return (this->value == c.value); }
bool large_float::operator<= (const large_float &c) const { return (this->value <= c.value); }
bool large_float::operator>  (const large_float &c) const { return (this->value >  c.value); }
bool large_float::operator>= (const large_float &c) const { return (this->value >= c.value); }
bool large_float::operator!= (const large_float &c) const { return (this->value != c.value); }

large_float large_float::neg() {
  large_float result;
  result.value = this->value*-1;
  return result;
}

std::string &large_float::to_string() {
  str_rep = value.str();
  return str_rep;
}

large_float::~large_float() {;}
