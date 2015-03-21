
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

#include <stdio.h>
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


int box::split_index() const
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

  return longest_idx;
}


box box::first(int index) const
{
  box left(value);

  large_float_t m = value[index].lower() + (value[index].upper() - value[index].lower())/2;
  left.value[index].assign(left.value[index].lower(), m);
  return left;
}


box box::second(int index) const
{
  box right(value);

  large_float_t m = value[index].lower() + (value[index].upper() - value[index].lower())/2;
  right.value[index].assign(m, right.value[index].upper());
  return right;
}


box box::midpoint() const
{
  box result(value);
  
  for (uint i = 0; i < value.size(); ++i) {
    large_float_t m = value[i].lower() + (value[i].upper() - value[i].lower())/2;
    result.value[i].assign(m, m);
  }
  
  return result;
}

interval box::operator[](int i)
{
  return interval(value.at(i));
}

std::string &box::to_string()
{
  if(str_rep != "")
    return str_rep;
  str_rep = "<";
  for(auto i : value) {
    str_rep += interval(i).to_string();
    str_rep += ", ";
  }
  str_rep += ">";
  return str_rep;
}


box::~box()
{
  ;
}
