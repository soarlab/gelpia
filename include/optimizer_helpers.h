
#ifndef OPTIMIZER_HELPERS_H
#define OPTIMIZER_HELPERS_H

#include "optimizer_types.h"

extern box_t left(std::vector<box_t> X_12) { return X_12[0];}
extern box_t right(std::vector<box_t> X_12) { return X_12[1];}
extern double upper(interval_t X) {return X.upper();}
extern double lower(interval_t X) {return X.lower();}
extern double point(box_t X) {return X[0].upper();}

extern interval_t func(box_t X){
  assert(X.size()==2);
 return -(pow(X[0],2)*12.0
	  - pow(X[0],4)*6.3
	  + pow(X[0],6)
	  + X[0]*X[1]*3.0
	  - pow(X[1],2)*12.0
	  + pow(X[1],4)*12.0);
}

/*
 * Creates a box with given dimentions, must be paired with a call to del_box
 * Arguments:
 *     mins - array of doubles for minimum values along intervals
 *     maxs - array of doubles for maximum values along intervals
 *     len  - number of dimentions
 * Return: new box
 */
extern box_t new_box();


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
