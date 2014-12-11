#include <boost/numeric/interval.hpp>
#include <vector>
#include <functional>
#include "harness.h"
using boost::numeric::interval;
using std::vector;
using std::function;

typedef interval<double> interval_t;
typedef vector<interval_t>  box_t;
typedef unsigned int uint;

/*
 * Divides given interval box along longest dimension
 * Arguments:
 *          X - given box
 * Return: vector of two new boxes
 */
vector<box_t> split_box(const box_t & X);


/*
 * Finds midpoint of given box
 * Arguments:
 *          X - given box
 * Return: box whose dimentions align to the single midpoint
 */
box_t midpoint(const box_t & X);

/*
 * Caluclates the width of the box, the length of the longest dimension
 * Arguments:
 *          X - given box
 * Return: width scalar
 */
double width(const box_t & X);


double width(const interval_t* X, size_t size);
/*
 * Divides given interval box along longest dimension
 * Arguments:
 *          X - given box
 * Return: vector of two new boxes
 */
vector<interval_t*> split_box(const interval_t* const X, size_t size);


/*
 * Finds midpoint of given box
 * Arguments:
 *          X - given box
 * Return: box whose dimentions align to the single midpoint
 */
interval_t* midpoint(const interval_t* const X, size_t size);

