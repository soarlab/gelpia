Global Extrema Locator Parallelization for Interval Arithmetic

Currently known to build on Ubuntu 14.04 through 16.04

Requirements:
  Not included:
    python3
      -ply
    bison
    flex
    c++ compiler
    c compiler
  Included:
    rust nightly
    gaol
    crlibm

For automatic building of included requirements run `make requirements`
For building by hand see documents/BuildingRequirements


Once requirements are met gelpia may be made by running `make`
This runs rust's cargo build system as well as adding the correct
files to bin for execution.


Gelpia may then be ran, it is an executable in the bin directory.
It has a built in help system for argument clarification.
A file may be specified which has arguments in it, one per line, this filename
must be preceded by an @ symbol. The benchmarks/fptaylor_generated directory has many of these
files. Additional arguments, or overwiting arguments, may be specified after the
file.

example uses:

> ./bin/gelpia @examples/gelpia_jet.txt
[119895.48836548299, {
'x2' : [4.993896484375, 5],
'x1' : [4.990234375, 5],

}]
Solver time: 0.21112608909606934
> ./bin/gelpia @examples/gelpia_jet.txt -ie 1e-15
[118943.03731237334, {
'x2' : [4.999999976716935, 5],
'x1' : [4.999999981373548, 5],

}]
Solver time: 0.34747815132141113