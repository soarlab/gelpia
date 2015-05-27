#include "box.h"


box::box()
{
  value = box_t();
}

box::box(const box &in)
{
  value = box_t();
  
  for (interval_t item : in.value) {
    value.emplace_back(interval_t(item.lower(), item.upper()));
  }
}

bool box::operator==(const box &c) const{
  if (this->size() != c.size()) {
    return false;
  }

  for (size_t i=0; i < (size_t)this->size(); i++) {
    if ((*this)[i] != c[i]) {
      return false;
    }
  }
  
  return true;
}

bool box::operator!=(const box &c) const{
  return !(*this == c);
}

int box::size() const { 
  return value.size(); 
}

const box_t & box::get_value() const { 
  return this->value; 
}

box::box(const box_t &in)
{
  value = box_t();

  for (interval_t item : in) {
    value.emplace_back(interval_t(item.lower(), item.upper()));
  }
}

int box::append(const std::string &low, const std::string &high)
{
  value.emplace_back(interval(low, high).get_value());
  return value.size();
}

int box::append(const interval &in)
{
  value.emplace_back(in.get_value());
  return value.size();
}

large_float box::width() const
{
  large_float_t largest(0.0);

  for (interval_t item : this->value) {
    if (largest < item.upper()-item.lower()) {
      largest = item.upper()-item.lower();
    }
  }
  
  return largest;
}

std::vector<box> box::split() const
{
  large_float_t longest(0.0);
  int longest_idx = 0;
  
  for(uint i = 0; i < value.size(); ++i) {
    auto len = value[i].upper() - value[i].lower();
    if(len > longest) {
      longest = len;
      longest_idx = i;
    }
  }

  box left(value);
  box right(value);
  large_float_t m = (value[longest_idx].lower() + value[longest_idx].upper())/2;
  left.value[longest_idx].assign(left.value[longest_idx].lower(), m);
  right.value[longest_idx].assign(m, right.value[longest_idx].upper());

  std::vector<box> retval = {left, right};
  return retval;
}

box box::midpoint() const
{
  box result(value);
  
  for (uint i = 0; i < value.size(); ++i) {
    large_float_t m = (value[i].lower() + value[i].upper())/2;
    result.value[i].assign(m, m);
  }
  
  return result;
}

interval box::operator[](int i) const
{
  return interval(value.at(i));
}

std::string &box::to_string()
{
  str_rep = "<";
  for(auto v : value) {
    str_rep += interval(v).to_string();
    str_rep += ", ";
  }
  str_rep += ">";
  return str_rep;
}

box::~box() {;}
