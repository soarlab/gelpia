#include <dlfcn.h>
#include <boost/numeric/interval.hpp>
#include <vector>
#include <boost/numeric/interval/rounded_transc.hpp>
#include <functional>
#include <iostream>
#include <cerrno>
#include <cstring>
#include <iostream>

using boost::numeric::interval;
using std::vector;
using boost::numeric::interval_lib::rounded_transc_exact;
using boost::numeric::interval_lib::policies;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::checking_strict;
typedef interval<double> box;
typedef vector<interval<double> > box_t;
typedef box gelpia_function_t(const box_t &);

class gelpia_func {
  gelpia_function_t* func;
  void* handle;
public:
  gelpia_func(std::string function_name)
  {
    // Extension is OS X specific. I believe Linux doesn't care about the extension.
    // This requires the library to by in the library path.
    // We will need to find a way to reliably set the library path.
    handle = dlopen(("lib"+function_name+".so").c_str(), RTLD_LAZY);
    if(!handle)
    {
      std::cout << dlerror() << std::endl;
      exit(1);
    }

    std::cout << "Handle at: " << (long*) handle << std::endl;
    
    func = (gelpia_function_t*)dlsym(handle, function_name.c_str());

    std::cout << "Function at: " << (long*) func << std::endl;
    
    if(!func)
    {
      std::cout << dlerror() << std::endl;
      exit(1);
    }
  }

  gelpia_function_t* get_function()
  {
    return func;
  }

  ~gelpia_func()
  {
    int result = dlclose(handle);
    if(result)
    {
      std::cout << dlerror() << std::endl;
      exit(1);
    }
    std::cout << "Released handle at: " << (long*) handle << ". Open count: " << result << std::endl;
  }
};

int main(int argc, const char* argv[])
{
  gelpia_func g = gelpia_func("f3");
  
  /*  void* handle;
  if(!(handle = dlopen("libf3.dylib", RTLD_LAZY)))
  {
    std::cout << strerror(errno) << "\n";
    std::cout << dlerror() << "\n";
    exit(1);
  }
  gelpia_function_t* f3;
  if(!(f3 = (gelpia_function_t*)dlsym(handle, "f3")))
  {
    std::cout << dlerror() << "\n";
    }*/

  box_t X(2);
  X[0] = interval<double>(0, 1);
  X[1] = interval<double>(0,3);

  std::cout << g.get_function()(X).upper() << std::endl;
  /*  std::cout << f3(X).upper() << std::endl;*/
}
