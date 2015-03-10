
#ifndef BOX_H
#define BOX_H

#include "large_float.h" 
#include "interval.h"

typedef std::vector<interval_t> box_t;


class box {
  box_t value;
  
 public:
  box();
  box(const box &in);
  box(const box_t &in);

  int append(const interval_t &in);
  
  large_float width();
  std::vector<box> split();
  box midpoint();
  
  ~box();
};

#endif
