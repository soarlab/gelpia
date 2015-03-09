
#ifndef BOX_H
#define BOX_H

#include "interval.h"


class box {
  std::vector<interval> my_box;
  
 public:
  box(const std::vector<interval> &in);
  box(const box &in);
  box(box &&in);
  box &operator=(const box &in);
  box &operator=(box &&in);

  box midpoint() const;
  std::vector<box> split() const;
  my_float width() const;
  
  ~box();
}

#endif
