#!/usr/bin/env python3

from pass_utils import *

import sys


def simplify(exp, inputs, assigns, consts=None):
  POWS = {"pow", "powi"}
  CV = {"Const", "Variable"}

  def _simplify(exp):
    tag = exp[0]

    if tag in BINOPS:
      l = _simplify(exp[1])
      r = _simplify(exp[2])
      if tag == "+":
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])+int(r[1])))
        # 0+x -> x
        if l == ("Integer", "0"):
          return r
        # x+0 -> x
        if r == ("Integer", "0"):
          return l
        # x+x -> 2*x
        if l == r:
          return ("*", ("Integer", "2"), l)
        # -x+y:
        #  if x==y -> 0
        #  else    -> y-x
        if l[0] == "neg":
          if l[1] == r:
            return ("Integer", "0")
          return ("-", r, l[1])
        # x+-y:
        #  if x==y -> 0
        #  else    -> x-y
        if r[0] == "neg":
          if r[1] == l:
            return ("Integer", "0")
          return ("-", l, r[1])
        # (x+y)+x -> (2*x)+y
        if l[0] == "+" and l[1] == r:
          return ("+", ("*", r, ("Integer", "2")), l[2])
        # (x+y)+y -> (2*y)+x
        if l[0] == "+" and l[2] == r:
          return ("+", ("*", r, ("Integer", "2")), l[1])
        # x+(x+y) -> (2*x)+y
        if r[0] == "+" and r[1] == l:
          return ("+", ("*", l, ("Integer", "2")), r[2])
        # x+(y+x) -> 2*x+y
        if r[0] == "+" and r[2] == l:
          return ("+", ("*", l, ("Integer", "2")), r[1])
        # (x-y)+x -> 2*x-y
        if l[0] == "-" and l[1] == r:
          return ("-", ("*", r, ("Integer", "2")), l[2])
        # (x-y)+y -> x
        if l[0] == "-" and l[2] == r:
          return l[1]
        # x+(x-y) -> 2*x-y
        if r[0] == "-" and r[1] == l:
          return ("-", ("*", l, ("Integer", "2")), r[2])
        # x+(y-x) -> y
        if r[0] == "-" and r[2] == l:
          return r[1]

      if tag == "-":
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])-int(r[1])))
        # 0-x -> -x
        if l == ("Integer", "0"):
          return ("neg", r)
        # x-0 -> x
        if r == ("Integer", "0"):
          return l
        # x-x -> 0
        if l == r:
          return ("Integer", "0")
        # x-(-y) -> x+y
        if r[0] == "neg":
          return ("+", l, r[1])

      if tag == "*":
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])*int(r[1])))
        # 1*x -> x
        if l == ("Integer", "1"):
          return r
        # x*1 -> x
        if r == ("Integer", "1"):
          return l
        # (-1)*x -> -x
        if l == ("Integer", "-1"):
          return ("neg", r)
        # x*(-1) -> -x
        if r == ("Integer", "-1"):
          return ("neg", l)
        # x*x -> x^2
        if r == l:
          return ("pow", l, ("Integer", "2"))
        # (x^n)*x -> x^(n+1)
        if l[0] == "pow" and l[1] == r:
          return ("pow", r, ("Integer", str(int(l[2][1])+1)))
        # x*(x^n) -> x^(n+1)
        if r[0] == "pow" and l == r[1]:
          return ("pow", l, ("Integer", str(int(r[2][1])+1)))
        # (x^n)*(x^m) -> x^(n+m)
        if r[0] == "pow" and l[0] == "pow" and l[1] == r[1]:
          return ("pow", l[1], ("Integer", str(int(l[2][1])+int(r[2][1]))))

      if tag in POWS:
        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
          return ("Integer", str(int(l[1])**int(r[1])))

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

      return (exp[0], arg)

    if tag == "Tuple":
      return (exp[0], _simplify(exp[1]), _simplify(exp[2]))

    if tag == "Return":
      return (exp[0], _simplify(exp[1]))

    if tag == "Variable":
      val = assigns[exp[1]]
      if val[0] in CV:
        return val
      return exp

    if tag == "Box":
      return ("Box",) + tuple(_simplify(b) for b in exp[1:])

    if tag in {"ConstantInterval", "InputInterval", "Float", "Integer",
               "Const", "Input", "Symbol", "PointInterval"}:
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
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)

  simplify(exp, inputs, assigns, consts)

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
