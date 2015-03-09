#include "rewrite.h"

/* Opens a library named as function_name.dylib (Should be configurable
   and gets the symbol for function_name within that library */
gelpia_func::gelpia_func(const std::string &function_name) {
  // Extension is OS X specific. I believe Linux doesn't care about the
  // extension. This requires the library to be in the library path or
  // the current directory.
  // We will need to find a way to reliably set the library path.
  handle = dlopen(("lib" + function_name + ".dylib").c_str(), RTLD_LAZY);
  if (!handle) {
    std::cout << dlerror() << std::endl;
    exit(1);
  }

  func = (gelpia_function_t *)dlsym(handle, function_name.c_str());

  if (!func) {
    std::cout << dlerror() << std::endl;
    exit(1);
  }
}

/* Returns the function for the gelpia_function object */
gelpia_function_t *gelpia_func::get_function() { return func; }

/* Closes the dynamic library, allowing the system to reclaim
   any resources used */
gelpia_func::~gelpia_func() {
  int result = dlclose(handle);
  if (result) {
    std::cout << dlerror() << std::endl;
    exit(1);
  }
}
