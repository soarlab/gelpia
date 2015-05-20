%module gelpia_utils
%{
#include "large_float.h"
#include "interval.h"
#include "box.h"
#include "function.h"

#include <boost/serialization/serialization.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <sstream>
%}

%include <std_string.i>
%include <std_vector.i>
%include "large_float.h"
%include "interval.h"
%ignore box::operator[];
%include "box.h"
%include "function.h"  

%extend large_float {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }

%extend interval {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }

%extend box {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }

  interval __getitem__(unsigned int i) {
    return (*self)[i];
  }
 }

namespace std {
  %template(BoxVector) vector<box>;
}

%define %boost_picklable(cls...)
%extend cls {
  std::string __getstate__()
    {
      std::stringstream ss;
      boost::archive::binary_oarchive ar(ss);
      ar << *($self);
      return ss.str();
              
    }

  void __setstate_internal(std::string const& sState)
  {
    std::stringstream ss(sState);
    boost::archive::binary_iarchive ar(ss);
    ar >> *($self);
            
  }

  %pythoncode %{
    def __setstate__(self, sState):
      self.__init__()
      self.__setstate_internal(sState)
  %}
      
 }
%enddef

%boost_picklable(large_float)
%boost_picklable(interval)

