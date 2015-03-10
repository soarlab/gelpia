
#include "box.h"

extern box first(std::vector<box> in) { return in[0];}
extern box second(std::vector<box> in) { return in[1];}

box::box()
{
  value = box_t();
}


box::box(const box &in)
{
  box::box(in.value);
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


large_float box::width() const
{
  large_float_t largest(-1);

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
    if((value[i].upper()-value[i].lower()) > longest) {
      longest = value[i].upper()-value[i].lower();
      longest_idx = i;
    }
  }

  // create two copies
  box X1(value);
  box X2(value);

  // split boxes along longest dimension
  large_float_t m = value[longest_idx].lower() + (value[longest_idx].upper() - value[longest_idx].lower())/2;
  X1.value[longest_idx].assign(X1.value[longest_idx].lower(), m);
  X2.value[longest_idx].assign(m, X2.value[longest_idx].upper());
  
  return std::vector<box>{X1, X2};
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


box::~box()
{
  ;
}
