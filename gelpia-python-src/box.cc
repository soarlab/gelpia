#include "box.h"

namespace bm = boost::multiprecision;

// Instantiate the box template
template box_t;

box::box()
{
  value = box_t();
}

box::box(const box &in)
{
  value = box_t();
  
  for (interval_t item : in.value) {
    value.emplace_back(interval_t(bm::lower(item), bm::upper(item)));
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

  for (const interval_t & item : in) {
    value.emplace_back(interval_t(bm::lower(item), bm::upper(item)));
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

  for (const interval_t & item : this->value) {
    if (largest < bm::width(item)) {
      largest = bm::width(item);
    }
  }
  
  return largest;
}

std::vector<box> box::split() const
{
  large_float_t longest(0.0);
  int longest_idx = 0;
  
  for(uint i = 0; i < value.size(); ++i) {
    auto len = bm::width(value[i]);
    if(len > longest) {
      longest = len;
      longest_idx = i;
    }
  }

  box left(value);
  box right(value);
  large_float_t m = bm::median(value[longest_idx]);
  left.value[longest_idx] = interval_t(bm::lower(left.value[longest_idx]), m);
  right.value[longest_idx] = interval_t(m, bm::upper(right.value[longest_idx]));

  std::vector<box> retval = {left, right};
  return retval;
}

box box::midpoint() const
{
  box result(value);
  
  for (uint i = 0; i < value.size(); ++i) {
    large_float_t m = bm::median(value[i]);
    result.value[i] = interval_t(m, m);
  }
  
  return result;
}

interval box::operator[](int i) const
{
  return interval(value.at(i));
}

const std::string &box::to_string() const
{
  // Lazily create the string
  if(str_rep == "") {
    str_rep = "<";
    for(const auto & v : value) {
      str_rep += interval(v).to_string();
      str_rep += ", ";
    }
    str_rep += ">";
  }
  return str_rep;
}

// Needed for SWIG
box::~box() {;}
