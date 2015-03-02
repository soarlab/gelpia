
%module optimizer_helpers
%{

#include "optimizer_types.h"
#include "optimizer_helpers.h"

%}

%include "carrays.i"
%array_class(double, doubleArray);
%include "optimizer_types.h"
%include "optimizer_helpers.h"
