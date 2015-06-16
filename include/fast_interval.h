#ifndef FAST_INTERVAL_H
#define FAST_INTERVAL_H

#include <string>
#include <boost/lexical_cast.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/split_free.hpp>
#include <sstream>
#include <iomanip>

#include <interval/interval.hpp> //Use filib++


typedef filib::interval<double> fast_interval_t;

// Enable Python pickling
namespace boost {
  namespace serialization {
    template <typename Archive>
      void save(Archive & ar, fast_interval_t const& in, const unsigned int version) {
      std::stringstream ls, us;
      ls << std::setprecision(17);
      ls << in.inf();
      us << std::setprecision(17);
      us << in.sup();
      
      std::string l, u;
      l = ls.str();
      u = us.str();

      ar & l;
      ar & u;
    }

    template <typename Archive>
      void load(Archive & ar, fast_interval_t & in, const unsigned version) {
      std::string l, u;
      ar & l;
      ar & u;
      in = fast_interval_t(strtod(l.c_str(),NULL), strtod(u.c_str(),NULL));
    }
    
    template<class Archive>
      inline void serialize(Archive & ar, fast_interval_t & t,
			    const unsigned int file_version) {
      split_free(ar, t, file_version);
    } 
  }
}

class fast_interval {
 private:
  friend class boost::serialization::access;
  fast_interval_t value;
  mutable std::string str_rep;

  template <typename Archive>
    void serialize(Archive & ar, const unsigned int version)
    {
      ar & value;
    }

 public:
  // Constructors
  fast_interval(const std::string &low_string, const std::string &high_string);
  fast_interval(const double &low, const double &high);
  fast_interval(const fast_interval &in);
  fast_interval(const fast_interval_t &in);
  fast_interval() {}

  // Operators
  bool operator==(const fast_interval &c) const;
  bool operator!=(const fast_interval &c) const;

  // Misc
  double width() const;
  double lower() const;
  double upper() const;
  std::string& to_string() const;
  fast_interval_t get_value() const;
  ~fast_interval();
};

fast_interval p2(const fast_interval & x);

#endif
