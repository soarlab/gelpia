#ifndef INTERVAL_H
#define INTERVAL_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/numeric/interval.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_member.hpp>

#include "large_float.h"


typedef boost::numeric::interval<large_float_t> interval_t;


class interval {
 private:
  friend class boost::serialization::access;
  interval_t value;
  std::string str_rep;

  template <typename Archive>
    void save(Archive & ar, const unsigned int version) const {
    std::string l,u;
    l = value.lower().str();
    u = value.upper().str();
    ar << l;
    ar << u;
  }

  template <typename Archive>
    void load(Archive & ar, const unsigned version) {
    std::string lower_str, upper_str;
    ar >> lower_str;
    ar >> upper_str;
    large_float_t lower, upper;
    lower = static_cast<large_float_t>(lower_str.c_str());
    upper = static_cast<large_float_t>(upper_str.c_str());
    value = interval_t(lower, upper);
  }

  BOOST_SERIALIZATION_SPLIT_MEMBER();

 public:
  // Constructors
  interval(const std::string &low_string, const std::string &high_string);
  interval(const large_float &low, const large_float &high);
  interval(const interval &in);
  interval(const interval_t &in);
  interval() {}

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
