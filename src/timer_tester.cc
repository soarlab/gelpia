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
int ITERS = 100;
/*
 * Times multiple executions of the given solver on the given function and 
 *     returns the average execution time
 *
 */
duration <double, std::nano> time_solver(solver_t solver,
				    function_t function,
				    int iters,
				    int solver_iters)
{
  auto start = high_resolution_clock::now();
  for (volatile auto i=0; i<iters; i++) {
    ; // do nothing (hopefully not opted away)
  }

  auto mid = high_resolution_clock::now();
  for (volatile auto i=0; i<iters; i++) {
    box_t X_0{interval<double>(-5,5), interval<double>(-5,5)};
    solver(X_0, EPSILON, EPSILON, solver_iters, function);
  }

  auto end = high_resolution_clock::now();

  auto diff = duration_cast<microseconds>(end-mid) - 
    duration_cast<microseconds>(mid-start);
  diff = diff/iters;
  return diff;
}



double test_solver(solver_t solver ,function_t function, double solution,
		 double epsilon, int solver_iters)
{
  box_t X_0{interval<double>(-5,5), interval<double>(-5,5)};
  auto actual = solver(X_0, EPSILON, EPSILON, solver_iters, function);
  return (std::abs(actual - solution));
}



int main(int argc, char* argv[])
{
  std::cout << "Function \t sequential_correct \t sequential_time \t par1_correct \t par1_time" << std::endl;
  for (auto function : FUNCTIONS) {
    std::cout << "function  \t ";
    box_t X_0{interval<double>(-5,5), interval<double>(-5,5)};
    auto solution = serial_solver(X_0, EPSILON, EPSILON, SOLVER_ITERS, function);
    for (auto solver : SOLVERS) {
      auto correct = test_solver(solver, function, solution, EPSILON,
			    SOLVER_ITERS);
      auto execution_time = time_solver(solver, function, ITERS, SOLVER_ITERS);
      std::cout << correct;
      std::cout << " \t\t\t ";
      std::cout << execution_time.count(); 
      std::cout << " \t\t ";
    }
    std::cout << std::endl;
  }
}

