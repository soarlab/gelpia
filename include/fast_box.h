#ifndef FAST_BOX_H
#define FAST_BOX_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>
#include <boost/serialization/vector.hpp>
#include <sstream>

#include "fast_interval.h"


typedef std::vector<fast_interval_t> fast_box_t;

class fast_box {
 private:
  friend class boost::serialization::access;
  fast_box_t value;
  mutable std::string str_rep;
  // For Python pickling
  template <typename Archive>
    void serialize(Archive & ar, const unsigned int version)
    {
      ar & value;
    }

 public:
  fast_box();
  fast_box(const fast_box &in);
  fast_box(const fast_box_t &in);

  // Operators
  bool operator==(const fast_box &c) const;
  bool operator!=(const fast_box &c) const;  

  int append(const std::string &low, const std::string &high);
  int append(const fast_interval &in);
  double width() const;
  std::vector<fast_box> split() const;
  fast_box midpoint() const;
  int size() const;
  const fast_box_t & get_value() const;
  fast_interval operator[] (int) const;
  const std::string& to_string() const;
  ~fast_box();
};


#endif
