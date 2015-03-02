
#ifndef OPTIMIZER_HELPERS_H
#define OPTIMIZER_HELPERS_H

#include "optimizer_types.h"

/*
 * Creates a box with given dimentions, must be paired with a call to del_box
 * Arguments:
 *     mins - array of doubles for minimum values along intervals
 *     maxs - array of doubles for maximum values along intervals
 *     len  - number of dimentions
 * Return: new box
 */
extern box_t new_box(double mins[], double maxs[], int length);


/*
 * Deletes given box and frees associated memory
 * Arguments:
 *     box - given box
 * Returns: Nothing
 */
extern void del_box(box_t box);


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
