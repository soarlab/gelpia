
#include <assert.h>
#include <stdio.h>
#include "box.h"

extern interval
function(const box &arg)
{
  const box_t X = arg.get_value();

  printf("%lu\n", X.size());
  assert(X.size() == 6);
  const interval_t &x1 = X[0],
    &x2 = X[1],
    &x3 = X[2],
    &x4 = X[3],
    &x5 = X[4],
    &x6 = X[5];
  
  return interval(x1*x4*(-x1 + x2 + x3 - x4 + x5 + x6) +
		  x2*x5*(x1 - x2 + x3 + x4 -x5 + x6) +
		  x3*x6*(x1 + x2 - x3 + x4 + x5 - x6)
		  -x2*x3*x4 - x1*x3*x5 - x1*x2*x6 -x4*x5*x6);
}
