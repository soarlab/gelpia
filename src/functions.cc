#include "harness.h"

using boost::numeric::interval;
using std::vector;


/*
* Testing interval function
*/
interval<double> F0(const box_t & X)
{
  assert(X.size()==2);
  return -(pow(X[0],2)*12.0 
    - pow(X[0],4)*6.3
    + pow(X[0],6) 
    + X[0]*X[1]*3.0
    - pow(X[1],2)*12.0
    + pow(X[1],4)*12.0);
}




/*
* Testing interval function
*/
interval<double> F1(const box_t & X)
{
  assert(X.size() == 2);
  interval<double> one(1.0,1.0);
  interval<double> result = X[0] * (one-X[0]) * (one-X[1]);
  return result;
}



