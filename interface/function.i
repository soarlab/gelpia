
%module function
%{
#include "large_float.h"
#include "interval.h"
#include "box.h"
#include "function.h"
  
%}

%include <std_string.i>
%include "large_float.h"
%include "interval.h"
%include "box.h"
%include "function.h"

%extend interval {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }

%extend box {
  interval __getitem__(int i)
  {
    return (*$self)[i];
  }
 }

%extend box {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }

%extend large_float {
  const char *__str__() {
    return (*$self).to_string().c_str();
  }
 }

%extend box {
  bool __lt__(const box& other)
  {
    return true;
  }
 }
