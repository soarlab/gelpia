
#ifndef OPTIMIZER_HELPERS_H
#define OPTIMIZER_HELPERS_H

#include "optimizer_types.h"

/*
 * Divides given interval box along longest dimension
 * Arguments:
 *          X - given box
 * Return: vector of two new boxes
 */
extern std::vector<box_t> split_box(const box_t & X);


/*
 * Finds midpoint of given box
 * Arguments:
 *          X - given box
 * Return: box whose dimentions align to the single midpoint
 */
extern box_t midpoint(const box_t & X);


/*
 * Caluclates the width of the box, the length of the longest dimension
 * Arguments:
 *          X - given box
 * Return: width scalar
 */
extern double width(const box_t & X);


#endif
