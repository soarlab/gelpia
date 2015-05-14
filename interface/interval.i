%module interval
%{
#include "large_float.h"
#include "interval.h"
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
