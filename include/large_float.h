#ifndef LARGE_FLOAT_H
#define LARGE_FLOAT_H


#include <boost/multiprecision/mpfr.hpp>
#include <string>


typedef boost::multiprecision::number<boost::multiprecision::mpfr_float_backend<300> >  large_float_t;


class large_float {
  large_float_t value;
  std::string str_rep;
  large_float() {}

 public:
  // Constructors
  large_float(const std::string &number);
  large_float(const large_float &in);
  large_float(large_float_t in);

  // Operators
  bool operator< (const large_float &c) const;
  bool operator==(const large_float &c) const;
  bool operator<=(const large_float &c) const;
  bool operator> (const large_float &c) const;
  bool operator>=(const large_float &c) const;
  bool operator!=(const large_float &c) const;

  // Misc.
  large_float neg();
  std::string &to_string();
  ~large_float();
};

#endif
