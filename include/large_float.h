#ifndef LARGE_FLOAT_H
#define LARGE_FLOAT_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/multiprecision/mpfr.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_member.hpp>


typedef boost::multiprecision::number<boost::multiprecision::mpfr_float_backend<300> >  large_float_t;


class large_float {
 private:
  friend class boost::serialization::access;
  large_float_t value;
  std::string str_rep;

  template <typename Archive>
    void save(Archive & ar, const unsigned int version) const {
    std::string tmp = value.str();
    ar << tmp;
  }

  template <typename Archive>
    void load(Archive & ar, const unsigned version) {
    std::string tmp;
    ar >> tmp;
    value = static_cast<large_float_t>(tmp.c_str());
  }

  BOOST_SERIALIZATION_SPLIT_MEMBER();

 public:
  // Constructors
  large_float(const std::string &number);
  large_float(const large_float &in);
  large_float(large_float_t in);
  large_float() {}

  // Operators
  bool operator< (const large_float &c) const;
  bool operator==(const large_float &c) const;
  bool operator<=(const large_float &c) const;
  bool operator> (const large_float &c) const;
  bool operator>=(const large_float &c) const;
  bool operator!=(const large_float &c) const;
  large_float operator- ();

  // Misc.
  std::string &to_string();
  large_float_t get_value() const;
  ~large_float();
};

#endif
