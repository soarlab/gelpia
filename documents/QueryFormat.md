

## Comments

Comments in query files use python syntax.
They are prfixed by a "#" character.


## Command line arguments

Command line arguments can be embedded in a query file by putting the argument in
a comment.
This comment must be the only text on the given line.
A function may not be specified as a flag this way.
Arguments given at the invocation of gelpia override those in the file.


## Intervals

Intervals are specified by `[<lower_value>, <upper_value>]` where the values are
floating point numbers or integers.
The lower bound must be less than or equal to the upper bound.


## Main Function

A function is a list of assignments and input specifiers  seperated by semicolons
followed by a list of expressions seperated by semicolons.
An input specifier is an interval followed by a variable name.
Assigning a variable to an interval also creates an input.
All expressions specified are summed and the exrema is found for this sum.


## Example

This query embedds in it that a minimum should be found.
It has two inputs, `x1` and `x2`, both have the range -32.768 to 32.768.
There are two expressions, so gelpia will find the minimum of their sum.

> # --mode=min
>
> [-32.768, 32.768] x1;
> [-32.768, 32.768] x2;
>
> 20 * exp(-0.2 * sqrt(((x1 - 5)^2 + (x2 - 5)^2) / 2));
> exp((cos(2*pi*(x1 - 5)) + cos(2*pi*(x2 - 5))) / 2);

Running gelpia on this example yields:

> \> ./bin/gelpia documents/example_1.dop
> Minimum lower bound 0.37836383188673656
> Minimum upper bound 0.468112869754073

