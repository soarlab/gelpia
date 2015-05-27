#ifndef BOX_H
#define BOX_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/numeric/interval.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>
#include <boost/serialization/vector.hpp>
#include <sstream>

#include "large_float.h" 
#include "interval.h"


typedef std::vector<interval_t> box_t;

class box {
 private:
  friend class boost::serialization::access;
  box_t value;
  std::string str_rep;

  template <typename Archive>
    void serialize(Archive & ar, const unsigned int version)
    {
      ar & value;
    }

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
  const box_t & get_value() const;
  interval operator[] (int) const;
  std::string& to_string();
  ~box();
};


#endif
