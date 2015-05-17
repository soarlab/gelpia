%module gelpia_utils
%{
#include "large_float.h"
#include "interval.h"
#include "box.h"
#include "function.h"  
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
