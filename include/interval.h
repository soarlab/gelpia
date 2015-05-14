#ifndef INTERVAL_H
#define INTERVAL_H


#include <boost/numeric/interval.hpp>
#include <boost/lexical_cast.hpp>
#include <string>

#include "large_float.h" 


typedef boost::numeric::interval<large_float_t> interval_t;


class interval {
  interval_t value;
  std::string str_rep;

 public:
  // Constructors
  interval(const std::string &low_string, const std::string &high_string);  
  interval(const interval &in);
  interval(const interval_t &in);

  // Operators
  bool operator==(const interval &c) const;
  bool operator!=(const interval &c) const;

  // Misc
  large_float width();
  large_float lower() const;
  large_float upper() const;
  std::string& to_string();
  interval_t get_value() const;
  ~interval();
};

#endif
