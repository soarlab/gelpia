#include "harness.h"
#include "functions.h"
#include "solvers.h"
#include <chrono>
#include <functional>
#include <vector>
#include <iostream>

using namespace std::chrono;
using namespace boost::numeric;

typedef std::function<interval<double>(box_t)> function_t;
typedef std::function<double (box_t, double, double, int, function_t)> solver_t;


std::vector<solver_t> SOLVERS{serial_solver, par1_solver};
std::vector<function_t> FUNCTIONS = {F0, F1};
double EPSILON = 0.00000000001;
int SOLVER_ITERS = 1000;


double test_solver(solver_t solver ,function_t function, double solution,
		 double epsilon, int solver_iters)
{
  box_t X_0{interval<double>(-5,5), interval<double>(-5,5)};
  auto actual = solver(X_0, EPSILON, EPSILON, solver_iters, function);
  return (std::abs(actual - solution));
}


int main(int argc, char* argv[])
{
  std::cout << "Function \t sequential_correct \t par1_correct \t par1_lockfree_correct" << std::endl;
  for (auto function : FUNCTIONS) {
    std::cout << "function  \t ";
    box_t X_0{interval<double>(-5,5), interval<double>(-5,5)};
    auto solution = serial_solver(X_0, EPSILON, EPSILON, SOLVER_ITERS, function);
    for (auto solver : SOLVERS) {
      auto correct = test_solver(solver, function, solution, EPSILON,
			    SOLVER_ITERS);
      std::cout << correct;
      std::cout << " \t\t ";
    }
    std::cout << std::endl;
  }
}
