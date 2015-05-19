%module interval
%{
#include "large_float.h"
#include "interval.h"

#include <boost/serialization/serialization.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <sstream>
%}

%include <std_string.i>
%include "large_float.h"
%include "interval.h"

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
