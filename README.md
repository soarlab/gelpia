# Global Extrema Locator Parallelization for Interval Arithmetic

## Gelpia algorithm
Gelpia is a cooperative, [interval-arithmetic](https://en.wikipedia.org/wiki/Interval_arithmetic) branch-and-bound based algorithm (IBBA). It rigorously finds an upper bound on the global maximum of a multivariate function on a given interval. This means that its answer is guaranteed to be above the global maximum on the interval when evaluated using real arithmetic.  
Gelpia is a ***cooperative*** solver in the sense that we concurrently run fast, approximate algorithms which find local maxima to inform the IBBA of new lower bounds. This causes the IBBA to refocus its attention on more promising regions of the search space. Meanwhile, the IBBA informs the cooperative algorithms of the search space currently being explored to keep them focused on trying to find the global maximum. We have found that this bi-directional communication significantly reduces runtime, allowing us to handle functions with many variables.

## Building and usage
Known to build on Ubuntu 14.04 through 16.04  
Currently only Linux is explicitly supported.

* Requirements:
	* Not included:
		* python3
			* ply
		* bison
		* flex
		* c++ compiler
		* c compiler
		* wget
	* Included:
		* rust nightly
		* gaol
		* crlibm

For automatic building of the requirements run `make requirements`  
For building by hand see _documents/BuildingRequirements_

Once requirements are met, gelpia may be compiled by running `make`  
This runs Rust's cargo build system as well as adding the correct
files to bin for execution.

Gelpia may then be ran, it is an executable `gelpia` in the `bin` directory.  
It has a built in help system for argument clarification.  
A file may be specified which has arguments in it, one per line, this filename
must be preceded by the **@** symbol. The _benchmarks/fptaylor\_generated_ directory has many of these files.  
Additional arguments, or overwiting arguments, may be specified after the
file.

#### Example uses:

> \>./bin/gelpia @benchmarks/fptaylor_generated/gelpia_jet.txt  
> [119895.48836548299, {  
> 'x2' : [4.993896484375, 5],  
> 'x1' : [4.990234375, 5],  
> }]    
> Solver time: 0.21112608909606934
>      
>  # Overriding input tolerance   
> \>./bin/gelpia @benchmarks/fptaylor_generated/gelpia_jet.txt -ie 1e-15  
> [118943.03731237334, {  
> 'x2' : [4.999999976716935, 5],  
> 'x1' : [4.999999981373548, 5],  
> }]  
> Solver time: 0.34747815132141113


### Dreal dOp format support
We currently support a subset of [Dreal's](https://github.com/dreal/dreal3) `dOp` optimizer input format. An example can be found at _benchmarks/dop\_benchmarks/pows.dop_. Full examples can be found in _benchmarks/dreal\_dop\_benchmarks_

#### An example run:  
> \>./bin/dop_gelpia benchmarks/dop_benchmarks/pows.dop   
> [390625, {  
> 'x' : [4.9990234375, 5],  
> }]  

> Parsing time: 0.07706475257873535   
> Solver time: 0.3199582099914551    

Gelpia's dOp mode cannot currently handle constraints as constraint propogation is not currently implemented.

## Issues
Gelpia may outlive the supplied time limit. This is because it goes through the remaining branches in the priority queue – this can sometimes be a lengthy process. This is why we have a **grace** option which is an additional grace period after the supplied timeout before gelpia is killed hard.  

When used for minimization, Gelpia will report a guaranteed lower bound on the global minimum.

## Authors
Gelpia is authored by Mark S. Baranowski and Ian Briggs
