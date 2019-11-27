An instruction sequnce is defined as:
inst_seq : inst
         | inst "," inst_seq

inst : "c" [0-9]+
     | "i" [0-9]+
     | "v" [0-9]+
     | "o" op
     | "f" func
     | "p" ("-"|"+")? [0-9]+

op   : "+" | "-" | "*" | "/" | "p"

func : "abs" | "cos" | "exp" | "log" | "neg" | "sin" | "tan" | "sqrt"

Instructions sequences are written in RPN. The behavior of each operation is
described below.

Push onto stack:
"c<num>" : Pushes a constant to the stack, <num> is an integer index into the
           constants array.
"i<num>" : Pushes a variabe to the stack, <num> is an integer index into the
           variables array.

Operators:
"o<op>" : Applies the operator <op> to the top two elements of the stack.
    	  <op> is in the set defined above, where p is interval exponent power
	  function.

Functions:
"f<name>" : Applies single arg function <name> to the top element of the  stack
            and pushes the result.

Integer power function:
"p<num>" : Applies the power function to the top of the stack with integer
           exponent <num> and pushes the result.

When an instruction sequence is consumed the result of the calculation is the
sole element remaining on the stack.
