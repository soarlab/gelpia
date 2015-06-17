#include "fast_box.h"


fast_box::fast_box()
{
  value = fast_box_t();
}

fast_box::fast_box(const fast_box &in)
{
  value = fast_box_t();
  
  for (fast_interval_t item : in.value) {
    value.emplace_back(fast_interval_t(item.inf(), item.sup()));
  }
}

fast_box::fast_box(const box &in)
{

  value = fast_box_t();
  
  for(const auto & item : in.get_value())
  {
    value.emplace_back(fast_interval_t(static_cast<double>(lower(item)),
				       static_cast<double>(upper(item))));
				       
  }  
}

bool fast_box::operator==(const fast_box &c) const{
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

bool fast_box::operator!=(const fast_box &c) const{
  return !(*this == c);
}

int fast_box::size() const { 
  return value.size(); 
}

const fast_box_t & fast_box::get_value() const { 
  return this->value; 
}

fast_box::fast_box(const fast_box_t &in)
{
  value = fast_box_t();

  for (const fast_interval_t & item : in) {
    value.emplace_back(fast_interval_t(item.inf(), item.sup()));
  }
}

int fast_box::append(const std::string &low, const std::string &high)
{
  value.emplace_back(fast_interval(low, high).get_value());
  return value.size();
}

int fast_box::append(const fast_interval &in)
{
  value.emplace_back(in.get_value());
  return value.size();
}

double fast_box::width() const
{
  double_t largest(0.0);

  for (const fast_interval_t & item : this->value) {
    if (largest < item.diam()) {
      largest = item.diam();
    }
  }
  
  return largest;
}

std::vector<fast_box> fast_box::split() const
{
  double_t longest(0.0);
  int longest_idx = 0;
  
  for(uint i = 0; i < value.size(); ++i) {
    auto len = value[i].diam();
    if(len > longest) {
      longest = len;
      longest_idx = i;
    }
  }

  fast_box left(value);
  fast_box right(value);
  double_t m = value[longest_idx].mid();
  left.value[longest_idx] = fast_interval_t(left.value[longest_idx].inf(), m);
  right.value[longest_idx] = fast_interval_t(m, right.value[longest_idx].sup());

  std::vector<fast_box> retval = {left, right};
  return retval;
}

fast_box fast_box::midpoint() const
{
  fast_box result(value);
  
  for (uint i = 0; i < value.size(); ++i) {
    double_t m = value[i].mid();
    result.value[i] = fast_interval_t(m, m);
  }
  
  return result;
}

fast_interval fast_box::operator[](int i) const
{
  return fast_interval(value.at(i));
}

const std::string &fast_box::to_string() const
{
  // Lazily create the string
  if(str_rep == "") {
    str_rep = "<";
    for(const auto & v : value) {
      str_rep += fast_interval(v).to_string();
      str_rep += ", ";
    }
    str_rep += ">";
  }
  return str_rep;
}

// Needed for SWIG
fast_box::~fast_box() {;}

