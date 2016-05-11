#include <gaol/gaol>
#include <iostream>
#include <string>

int main() {
  std::string s;
  std::getline(std::cin, s);
  try {
    std::cout << gaol::interval(s.c_str()) << std::endl;
  }
  catch(...) {
    return 1;
  }
  return 0;
}
