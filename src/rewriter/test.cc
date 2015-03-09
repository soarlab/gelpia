#include <iostream>
#include "gelpia_func.h"

typedef std::function<boost::numeric::interval<double>(box_t)> function_t;
box eval_function(const function_t& f, const box_t& X)
{
  return f(X);
}

int main(int argc, const char* argv[])
{
  //  gelpia_func g = gelpia_func("f1");
  
  box_t X(2);
  X[0] = interval<double>(0, 1);
  X[1] = interval<double>(0,3);

  std::cout << eval_function(gelpia_func("f1"), X).upper() << std::endl;
}
