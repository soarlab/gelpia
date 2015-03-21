
%module box
%{
#include "large_float.h"
#include "interval.h"
#include "box.h"
  
%}

%include <std_string.i>
%include "large_float.h"
%include "interval.h"
%include "box.h"

%rename (__getitem__) box::operator[](size_t index);

%extend box {
  interval __getitem__(int t)
  {
    return (*$self)[t];
  }
 }
