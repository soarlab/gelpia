// HEADER FILE FOR GENERATED FUNCTIONS
#include <boost/numeric/interval.hpp>
#include <vector>
#include <boost/numeric/interval/rounded_transc.hpp>

using boost::numeric::interval;
using std::vector;
using boost::numeric::interval_lib::rounded_transc_exact;
using boost::numeric::interval_lib::policies;
using boost::numeric::interval_lib::rounded_math;
using boost::numeric::interval_lib::checking_strict;

typedef vector<interval<double>> box_t;

// FUN_NAME is to be set as a macro definition by the compiler to enable the
// symbol to have a unique name
extern "C" interval<double> FUN_NAME(const box_t &x) {
