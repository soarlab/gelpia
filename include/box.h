#ifndef BOX_H
#define BOX_H


#include "large_float.h" 
#include "interval.h"


typedef std::vector<interval_t> box_t;


class box {
  box_t value;
  std::string str_rep;

 public:
  box();
  box(const box &in);
  box(const box_t &in);

  // Operators
  bool operator==(const box &c) const;
  bool operator!=(const box &c) const;  

  int append(const std::string &low, const std::string &high);
  int append(const interval &in);
  large_float width() const;
  std::vector<box> split() const;
  box midpoint() const;
  int size() const;
  box_t get_value() const;
  interval operator[] (int) const;
  std::string& to_string();
  ~box();
};


#endif
