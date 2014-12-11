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

typedef std::function<interval<double>(interval_t*, size_t)> function_p_t;
typedef std::function<double (box_t, double, double, int, function_p_t)> solver_p_t;

std::vector<solver_t> SOLVERS{serial_solver, par1_solver};
std::vector<solver_p_t> P_SOLVERS = {};
std::vector<function_t> FUNCTIONS = {F0, F1};
std::vector<function_p_t> P_FUNCTIONS = {F0_p, F1_p};

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

duration <double, std::nano> time_solver(solver_p_t solver,
				    function_p_t function,
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



int main(int argc, char* argv[])
{
  std::cout << "Function \t sequential_time \t par1_time \t par1_lockfree_time" << std::endl;
  for (int f_index=0; f_index< FUNCTIONS.size(); f_index++) {
    std::cout << "function  \t ";

    for (auto solver : SOLVERS) {
      auto execution_time = time_solver(solver, FUNCTIONS[f_index], ITERS, SOLVER_ITERS);
      std::cout << execution_time.count(); 
      std::cout << " \t\t ";
    }

    for (auto solver : P_SOLVERS) {
      auto execution_time = time_solver(solver, P_FUNCTIONS[f_index], ITERS, SOLVER_ITERS);
      std::cout << execution_time.count(); 
      std::cout << " \t\t ";
    }
    std::cout << std::endl;
  }
}

