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


std::vector<solver_t> SOLVERS{serial_solver, par1_solver, sol2_solver};
std::vector<solver_p_t> P_SOLVERS{};
std::vector<function_t> FUNCTIONS = {F0, F1};
std::vector<function_p_t> P_FUNCTIONS = {F0_p, F1_p};
double EPSILON = 0.00000000001;
int SOLVER_ITERS = 10000;
int num_threads;

double test_solver(solver_t solver ,function_t function, double solution,
		 double epsilon, int solver_iters)
{
  box_t X_0{interval<double>(-100000,100000), interval<double>(-100000,100000)};
  auto actual = solver(X_0, EPSILON, EPSILON, solver_iters, function);
  return (std::abs(actual - solution));
}

double test_solver(solver_p_t solver ,function_p_t function, double solution,
		 double epsilon, int solver_iters)
{
  box_t X_0{interval<double>(-100000,100000), interval<double>(-100000,100000)};
  auto actual = solver(X_0, EPSILON, EPSILON, solver_iters, function);
  return (std::abs(actual - solution));
}


int main(int argc, char* argv[])
{
  num_threads = 2;
  std::cout << "Function, TrueSolution, sequ, par1, sol2" << std::endl;
  for (int f_index=0; f_index< FUNCTIONS.size(); f_index++) {
    std::cout << "function , ";
    box_t X_0{interval<double>(-100000,100000), interval<double>(-100000,100000)};
    auto solution = serial_solver(X_0, EPSILON, EPSILON, SOLVER_ITERS, FUNCTIONS[f_index]);
    std::cout << solution;
    std::cout << ", ";
    for (auto solver : SOLVERS) {
      auto correct = test_solver(solver, FUNCTIONS[f_index], solution, EPSILON,
			    SOLVER_ITERS);
      std::cout << correct;
      std::cout << ", ";
    }

    for (auto solver : P_SOLVERS) {
      auto correct = test_solver(solver, P_FUNCTIONS[f_index], solution, EPSILON,
			    SOLVER_ITERS);
      std::cout << correct;
      std::cout << ", ";
    }
    std::cout << std::endl;
  }
}
