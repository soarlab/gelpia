#ifndef LARGE_FLOAT_H
#define LARGE_FLOAT_H


#include <boost/multiprecision/mpfr.hpp>
#include <string>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>

typedef boost::multiprecision::number<boost::multiprecision::mpfr_float_backend<300> >  large_float_t;

class large_float {
 public:
  large_float_t value;
  std::string str_rep;
  large_float() {}
  // public:
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

namespace boost {
  namespace serialization {
    template <typename Archive>
    void save(Archive& ar, const large_float& r, unsigned version)
    {
      std::string tmp = r.value.str();// 0 indicates use full precision
      ar & tmp;
    }

    template <typename Archive>
    void load(Archive& ar, large_float& r, unsigned version)
    {
      std::string tmp;
      ar & tmp;
      r = large_float(tmp.c_str());
    }
    
    template<class Archive>
      void serialize(Archive & ar,
		     large_float& r,
		     const unsigned int file_version){
      boost::serialization::split_free(ar, r, file_version);
    }
  }
}

#endif
