#ifndef INTERVAL_H
#define INTERVAL_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/numeric/interval.hpp>
#include <boost/multiprecision/mpfi.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>
#include <sstream>

#include "large_float.h"

/*using boost::numeric::interval_lib::policies;
using boost::numeric::interval_lib::save_state;
using boost::numeric::interval_lib::rounded_transc_exact;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::checking_strict;*/

using boost::multiprecision::mpfi_float_backend;
using boost::multiprecision::number;

// Needed for transcendental function support.
// Todo: Switch to MPFI or another interval library since the sine/cosine
// functions return very wide intervals which is not useful for our purpose.
//typedef boost::numeric::interval<large_float_t,
//  policies<save_state<rounded_transc_exact<large_float_t, rounded_math<large_float_t> > >,
//  checking_strict<large_float_t> > > interval_t;

typedef number<mpfi_float_backend<300> > interval_t;

// Enable Python pickling
namespace boost {
  namespace serialization {
    template <typename Archive>
      void save(Archive & ar, interval_t const& in, const unsigned int version) {
      large_float_t l,u;
      l = lower(in);
      u = upper(in);
      ar << l;
      ar << u;
    }

    template <typename Archive>
      void load(Archive & ar, interval_t & in, const unsigned version) {
      large_float_t lower, upper;
      ar >> lower;
      ar >> upper;
      in = interval_t(lower, upper);
    }
    
    template<class Archive>
      inline void serialize(Archive & ar, interval_t & t,
			    const unsigned int file_version) {
      split_free(ar, t, file_version);
    } 
  }
}

class interval {
 private:
  friend class boost::serialization::access;
  interval_t value;
  mutable std::string str_rep;

  template <typename Archive>
    void serialize(Archive & ar, const unsigned int version)
    {
      ar & value;
    }

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
  large_float width() const;
  large_float lower() const;
  large_float upper() const;
  std::string& to_string() const;
  interval_t get_value() const;
  ~interval();
};

#endif
