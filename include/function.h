
#ifndef FUNCTION_H
#define FUNCTION_H

#include "large_float.h" 
#include "interval.h"
#include "box.h"
#include "fast_interval.h"
#include "fast_box.h"

extern interval function(const box & X_wrapped);

extern fast_interval fast_function(const fast_box & X_wrapped);
#endif
