#ifndef LARGE_FLOAT_H
#define LARGE_FLOAT_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/multiprecision/mpfr.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>
#include <sstream>

typedef boost::multiprecision::number<boost::multiprecision::mpfr_float_backend<300> >  large_float_t;

// Needed for Python pickling
namespace boost {
  namespace serialization {
    template <typename Archive>
      void save(Archive & ar, large_float_t const& r, const unsigned int version) {
      std::string tmp = r.str();
      ar << tmp;
    }

    template <typename Archive>
      void load(Archive & ar, large_float_t & r, const unsigned version) {
      std::string tmp;
      ar >> tmp;
      r = static_cast<large_float_t>(tmp.c_str());
    }

    template<class Archive>
      inline void serialize(Archive & ar, large_float_t & t,
			    const unsigned int file_version) {
      split_free(ar, t, file_version);
    }
  }
}


class large_float {
 private:
  friend class boost::serialization::access;
  large_float_t value;
  // Lazily initialized value for the string representation of the large_float
  std::string str_rep;

  template <typename Archive>
    void serialize(Archive & ar, const unsigned int version)
    {
      ar & value;
    }

 public:
  // Constructors
  large_float(const std::string &number);
  large_float(const large_float &in);
  large_float(const large_float_t &in);
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
