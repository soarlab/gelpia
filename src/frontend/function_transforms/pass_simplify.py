#!/usr/bin/env python3

import sys

from pass_utils import *
from pass_lift_consts import lift_consts

def simplify(exp, inputs, assigns, consts=None):
  """ Applies algebraic simplifications to the expression """

  # Constants
  NEG_ONE     = ("Integer", "-1")
  ZERO        = ("Integer", "0")
  ONE         = ("Integer", "1")
  TWO         = ("Integer", "2")

  POWS        = {"pow", "powi"}
  C_OR_V      = {"Const", "Variable"}
  PASSTHROUGH = {"ConstantInterval", "InputInterval", "Float", "Integer",
                 "Const", "Input", "Symbol", "PointInterval"}
  import inspect

  def p_log(func):
    start = len(inspect.stack())
    stack = list()
    def wrap(exp):
      input = exp
      output = func(exp)
      d = len(inspect.stack())-start
      if input != output:
        stack.append(d*"   "+"{} -> {}".format(input, output))
      else:
        stack.append(d*"   "+str(input))
      if d==0:
        stack.reverse()
        for s in stack:
          print(s)
      return output
    return wrap


  def _simplify(exp):
    tag = exp[0]

    if tag in BINOPS:
      l = _simplify(exp[1])
      r = _simplify(exp[2])

      if tag == "+":
        # work = [l, r]
        # madd = list()
        # while len(work) > 0:
        #   item = work.pop()
        #   if item[0] == "+":
        #     work.append(item[1])
        #     work.append(item[2])
        #   else:
        #     madd.append(item)

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])+int(r[1])))

        # 0 + x -> x
        if l == ZERO:
          return r
        # x + 0 -> x
        if r == ZERO:
          return l

        # x + x -> 2*x
        if l == r:
          return ("*", TWO, l)

        # (-x) + y:
        #  if x==y -> 0
        #  else    -> y-x
        if l[0] == "neg":
          if l[1] == r:
            return ZERO
          return ("-", r, l[1])
        # x + (-y):
        #  if x==y -> 0
        #  else    -> x-y
        if r[0] == "neg":
          if r[1] == l:
            return ZERO
          return ("-", l, r[1])

        # (x+y) + x -> (2*x)+y
        if l[0] == "+" and l[1] == r:
          return ("+", ("*", r, TWO), l[2])
        # (x+y) + y -> (2*y)+x
        if l[0] == "+" and l[2] == r:
          return ("+", ("*", r, TWO), l[1])
        # x + (x+y) -> (2*x)+y
        if r[0] == "+" and r[1] == l:
          return ("+", ("*", l, TWO), r[2])
        # x + (y+x) -> (2*x)+y
        if r[0] == "+" and r[2] == l:
          return ("+", ("*", l, TWO), r[1])

        # (x-y) + x -> (2*x)-y
        if l[0] == "-" and l[1] == r:
          return ("-", ("*", r, TWO), l[2])
        # (x-y) + y -> x
        if l[0] == "-" and l[2] == r:
          return l[1]
        # x + (x-y) -> (2*x)-y
        if r[0] == "-" and r[1] == l:
          return ("-", ("*", l, TWO), r[2])
        # x + (y-x) -> y
        if r[0] == "-" and r[2] == l:
          return r[1]

        # x + (n*x) -> (n+1)*x
        if r[0] == "*" and l == r[2]:
          if r[1][0] == "Integer":
            return ("*", ("Integer", str(int(r[1][1])+1)), l)
          return ("*", ("+", r[1], ONE), l)
        # x + (x*n) -> (n+1)*x
        if r[0] == "*" and l == r[1]:
          if r[2][0] == "Integer":
            return ("*", ("Integer", str(int(r[2][1])+1)), l)
          return ("*", ("+", r[2], ONE), l)
        # (n*x) + x -> (n+1)*x
        if l[0] == "*" and r == l[2]:
          if l[1][0] == "Integer":
            return ("*", ("Integer", str(int(l[1][1])+1)), r)
          return ("*", ("+", l[1], ONE), r)
        # (x*n) + x -> (n+1)*x
        if l[0] == "*" and r == l[1]:
          if l[2][0] == "Integer":
            return ("*", ("Integer", str(int(l[2][1])+1)), r)
          return ("*", ("+", l[2], ONE), r)


      if tag == "-":
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])-int(r[1])))

        # 0 - x -> -x
        if l == ZERO:
          return ("neg", r)
        # x - 0 -> x
        if r == ZERO:
          return l

        # x - x -> 0
        if l == r:
          return ZERO

        # x - (-y):
        #  if x==y -> 2*x
        #  else    -> x+y
        if r[0] == "neg":
          if l == r[1]:
            return ("*", TWO, l)
          return ("+", l, r[1])
        # (-x) - y
        #  if x==y -> -(2*x)
        #  else    -> -(x+y)
        if r[0] == "neg":
          if l[1] == r:
            return ("neg", ("*", TWO, l))
          return ("neg", ("+", l[1], r))

        # x - (x+y) -> -y
        if r[0] == "+" and l == r[1]:
          return ("neg", r[2])
        # x - (y+x) -> -y
        if r[0] == "+" and l == r[2]:
          return ("neg", r[1])
        # (x+y) - x -> y
        if l[0] == "+" and l[1] == r:
          return l[2]
        # (x+y) - y -> x
        if l[0] == "+" and l[2] == r:
          return l[1]

        # x - (x-y) -> y
        if r[0] == "-" and l == r[1]:
          return r[2]
        # x - (y-x) -> (2*x)-y
        if r[0] == "-" and l == r[2]:
          return ("-", ("*", TWO, l), r[1])
        # (x-y) - x -> -y
        if l[0] == "-" and l[1] == r:
          return ("neg", l[2])
        # (x-y) - y -> x-(2*y)
        if l[0] == "+" and l[2] == r:
          return ("-", l[1], ("*", TWO, r))

        # x - (n*x) -> (n-1)*x
        if r[0] == "*" and l == r[2]:
          if r[1][0] == "Integer":
            return ("*", ("Integer", str(int(r[1][1])-1)), l)
          return ("*", ("-", r[1], ONE), l)
        # x - (x*n) -> (n-1)*x
        if r[0] == "*" and l == r[1]:
          if r[2][0] == "Integer":
            return ("*", ("Integer", str(int(r[2][1])-1)), l)
          return ("*", ("-", r[2], ONE), l)
        # (n*x) - x -> (n-1)*x
        if l[0] == "*" and r == l[2]:
          if l[1][0] == "Integer":
            return ("*", ("Integer", str(int(l[1][1])-1)), r)
          return ("*", ("-", l[1], ONE), r)
        # (x*n) - x -> (n-1)*x
        if l[0] == "*" and r == l[1]:
          if l[2][0] == "Integer":
            return ("*", ("Integer", str(int(l[2][1])-1)), r)
          return ("*", ("-", l[2], ONE), r)


      if tag == "*":
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])*int(r[1])))

        # 1 * x -> x
        if l == ONE:
          return r
        # x * 1 -> x
        if r == ONE:
          return l

        # (-1) * x -> -x
        if l == NEG_ONE:
          return ("neg", r)
        # x * (-1) -> -x
        if r == NEG_ONE:
          return ("neg", l)

        # x * x -> x^2
        if r == l:
          return ("pow", l, TWO)

        # (x^n) * x -> x^(n+1)
        if l[0] == "pow" and l[1] == r:
          return ("pow", r, ("Integer", str(int(l[2][1])+1)))
        # x * (x^n) -> x^(n+1)
        if r[0] == "pow" and l == r[1]:
          return ("pow", l, ("Integer", str(int(r[2][1])+1)))
        # (x^n) * (x^m) -> x^(n+m)
        if r[0] == "pow" and l[0] == "pow" and l[1] == r[1]:
          return ("pow", l[1], ("Integer", str(int(l[2][1])+int(r[2][1]))))


      if tag in POWS:
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])**int(r[1])))

        # x ^ 1 -> x
        if r == ONE:
          return l

        # abs(x) ^ (2*n) -> x^(2*n)
        if l[0] == "abs" and r[0] == "Integer" and int(r[1])%2==0:
          return (exp[0], l[1], r)

        # (-x) ^ (2*n) -> x^(2*n)
        if l[0] == "neg" and r[0] == "Integer" and int(r[1])%2==0:
          return (exp[0], l[1], r)

      return (exp[0], l, r)



    if tag in UNOPS:
      arg = _simplify(exp[1])

      if tag == "neg":
        # Collapse integer expressions
        if arg[0] == "Integer":
          return ("Integer", str(-int(arg[1])))

        # -(-x) -> x
        if arg[0] == "neg":
          return arg[1]


      if tag == "abs":
        # Collapse integer expressions
        if arg[0] == "Integer":
          return ("Integer", str(abs(int(arg[1]))))

        # abs(-x)     -> abs(x)
        # abs(abs(x)) -> abs(x)
        if arg[0] == "neg" or arg[0] == "abs":
          return (exp[0], arg[1])

        # abs(x^(2*n)) -> x^2n
        if arg[0] == "pow" and int(arg[2][1])%2 == 0:
          return arg


      if tag == "cos":
        # cos(-x) -> cos(x)
        if arg[0] == "neg":
          return (exp[0], arg[1])

      if tag == "cosh":
        # cosh(-x) -> cosh(x)
        if arg[0] == "neg":
          return (exp[0], arg[1])

      return (exp[0], arg)


    if tag == "Tuple":
      return (exp[0], _simplify(exp[1]), _simplify(exp[2]))

    if tag == "Return":
      return (exp[0], _simplify(exp[1]))

    if tag == "Variable":
      val = assigns[exp[1]]
      if val[0] in C_OR_V:
        return val
      return exp

    if tag == "Box":
      return ("Box",) + tuple(_simplify(b) for b in exp[1:])

    if tag in PASSTHROUGH:
      return exp

    print("simplify error unknown: '{}'".format(exp))
    sys.exit(-1)


  for var,val in assigns.items():
    assigns[var] = _simplify(val)
  new_exp =  _simplify(exp)

  return new_exp











def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  exp = simplify(exp, inputs, assigns)
  e, exp, consts = lift_consts(exp, inputs, assigns)

  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_assigns(assigns)
  print()
  print_consts(consts)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
