
%module large_float
%{

#include "large_float.h"

%}

%include <std_string.i>
%include "large_float.h"

%extend large_float {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }
