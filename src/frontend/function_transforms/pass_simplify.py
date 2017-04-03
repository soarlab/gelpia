#!/usr/bin/env python3

import sys

from pass_utils import *
from pass_lift_consts import lift_consts
from expression_walker import walk

import ian_utils as iu

def simp(func):
  iu.log(3, lambda : iu.cyan("SIMP: ") + func())

def simplify(exp, inputs, assigns, consts=None):
  """ Applies algebraic simplifications to the expression """

  # Constants
  C_OR_V      = {"Const", "Variable"}
  NEG_ONE     = ("Integer", "-1")
  ZERO        = ("Integer", "0")
  ONE         = ("Integer", "1")
  TWO         = ("Integer", "2")

  def _add(work_stack, count, args):
    assert(args[0] == "+")
    assert(len(args) == 3)
    l, r = args[1], args[2]

    # Collapse integer expressions
    if l[0] == "Integer" and r[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(int(l[1])+int(r[1])))))
      return

    # 0 + x -> x
    if l == ZERO:
      work_stack.append((True, count, r))
      simp(lambda :"Eliminated Zero in add")
      return
    # x + 0 -> x
    if r == ZERO:
      work_stack.append((True, count, l))
      simp(lambda :"Eliminated Zero in add")
      return

    # x + x -> 2*x
    if l == r:
      work_stack.append((True, count, ("*", TWO, l)))
      simp(lambda :"x + x -> 2*x\n\tx = {}".format(l))
      return

    # (-x) + y:
    #  if x==y -> 0
    #  else    -> y-x
    if l[0] == "neg":
      if l[1] == r:
        work_stack.append((True, count, ZERO))
        simp(lambda :"(-x) + x -> 0\n\tx = {}".format(r))
        return
      work_stack.append((True, count, ("-", r, l[1])))
      simp(lambda :"(-x) + y -> y-x\n\tx = {}\n\ty = {}".format(l[1], r))
      return
    # x + (-y):
    #  if x==y -> 0
    #  else    -> x-y
    if r[0] == "neg":
      if r[1] == l:
        work_stack.append((True, count, ZERO))
        simp(lambda :"x + (-x) -> 0\n\tx = {}".format(l))
        return
      work_stack.append((True, count, ("-", l, r[1])))
      simp(lambda :"x + (-y) -> x-y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return

    # (x+y) + x -> (2*x)+y
    if l[0] == "+" and l[1] == r:
      work_stack.append((True, count,  ("+", ("*", r, TWO), l[2])))
      simp(lambda :"(x+y) + x -> (2*x)+y\n\tx = {}\n\ty = {}".format(r, l[2]))
      return
    # (x+y) + y -> (2*y)+x
    if l[0] == "+" and l[2] == r:
      work_stack.append((True, count,  ("+", ("*", r, TWO), l[1])))
      simp(lambda :"(x+y) + y -> (2*y)+x\n\tx = {}\n\ty = {}".format(l[1], r))
      return
    # x + (x+y) -> (2*x)+y
    if r[0] == "+" and r[1] == l:
      work_stack.append((True, count,  ("+", ("*", l, TWO), r[2])))
      simp(lambda :"x + (x+y) -> (2*x)+y\n\tx = {}\n\ty = {}".format(l, r[2]))
      return
    # x + (y+x) -> (2*x)+y
    if r[0] == "+" and r[2] == l:
      work_stack.append((True, count,  ("+", ("*", l, TWO), r[1])))
      simp(lambda :"x + (y+x) -> (2*x)+y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return

    # (x-y) + x -> (2*x)-y
    if l[0] == "-" and l[1] == r:
      work_stack.append((True, count,  ("-", ("*", r, TWO), l[2])))
      simp(lambda :"(x-y) + x -> (2*x)-y\n\tx = {}\n\ty = {}".format(r, l[2]))
      return
    # (x-y) + y -> x
    if l[0] == "-" and l[2] == r:
      work_stack.append((True, count,  l[1]))
      simp(lambda :"(x-y) + y -> x\n\tx = {}\n\ty = {}".format(l[1], r))
      return
    # x + (x-y) -> (2*x)-y
    if r[0] == "-" and r[1] == l:
      work_stack.append((True, count,  ("-", ("*", l, TWO), r[2])))
      simp(lambda :"x + (x-y) -> (2*x)-y\n\tx = {}\n\ty = {}".format(l, r[2]))
      return
    # x + (y-x) -> y
    if r[0] == "-" and r[2] == l:
      work_stack.append((True, count,  r[1]))
      simp(lambda :"x + (y-x) -> y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return

    # x + (n*x) -> (n+1)*x
    if r[0] == "*" and l == r[2]:
      simp(lambda :"x + (n*x) -> (n+1)*x\n\tx = {}".format(l))
      if r[1][0] == "Integer":
        work_stack.append((True, count,  ("*", ("Integer", str(int(r[1][1])+1)), l)))
        return
      work_stack.append((True, count,  ("*", ("+", r[1], ONE), l)))
      return
    # x + (x*n) -> (n+1)*x
    if r[0] == "*" and l == r[1]:
      simp(lambda :"x + (x*n) -> (n+1)*x\n\tx = {}".format(l))
      if r[2][0] == "Integer":
        work_stack.append((True, count,  ("*", ("Integer", str(int(r[2][1])+1)), l)))
        return
      work_stack.append((True, count,  ("*", ("+", r[2], ONE), l)))
      return
    # (n*x) + x -> (n+1)*x
    if l[0] == "*" and r == l[2]:
      simp(lambda :"(n*x) + x-> (n+1)*x\n\tx = {}".format(r))
      if l[1][0] == "Integer":
        work_stack.append((True, count,  ("*", ("Integer", str(int(l[1][1])+1)), r)))
        return
      work_stack.append((True, count,  ("*", ("+", l[1], ONE), r)))
      return
    # (x*n) + x -> (n+1)*x
    if l[0] == "*" and r == l[1]:
      simp(lambda :"(x*n) + x-> (n+1)*x\n\tx = {}".format(r))
      if l[2][0] == "Integer":
        work_stack.append((True, count,  ("*", ("Integer", str(int(l[2][1])+1)), r)))
        return
      work_stack.append((True, count,  ("*", ("+", l[2], ONE), r)))
      return

    work_stack.append((True, count, tuple(args)))


  def _sub(work_stack, count, args):
    assert(args[0] == "-")
    assert(len(args) == 3)
    l, r = args[1], args[2]

    # Collapse integer expressions
    if l[0] == "Integer" and r[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(int(l[1])-int(r[1])))))
      return

    # 0 - x -> -x
    if l == ZERO:
      work_stack.append((True, count, ("neg", r)))
      simp(lambda :"Eliminated Zero in subtract")
      return
    # x - 0 -> x
    if r == ZERO:
      work_stack.append((True, count, l))
      simp(lambda :"Eliminated Zero in subtract")
      return

    # x - x -> 0
    if l == r:
      work_stack.append((True, count, ZERO))
      simp(lambda :"x - x -> 0\n\tx = {}".format(l))
      return

    # x - (-y):
    #  if x==y -> 2*x
    #  else    -> x+y
    if r[0] == "neg":
      if l == r[1]:
        work_stack.append((True, count, ("*", TWO, l)))
        simp(lambda :"x - (-x) -> 2*x\n\tx = {}".format(l))
        return
      work_stack.append((True, count, ("+", l, r[1])))
      simp(lambda :"x - (-y) -> x+y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return
    # (-x) - y
    #  if x==y -> -(2*x)
    #  else    -> -(x+y)
    if r[0] == "neg":
      if l[1] == r:
        work_stack.append((True, count, ("neg", ("*", TWO, l))))
        simp(lambda :"(-x) - x -> -(2*x)\n\tx = {}".format(r))
        return
      work_stack.append((True, count, ("neg", ("+", l[1], r))))
      simp(lambda :"(-x) - y -> -(x+y)\n\tx = {}\n\ty = {}".format(l[1], r))
      return

    # x - (x+y) -> -y
    if r[0] == "+" and l == r[1]:
      work_stack.append((True, count, ("neg", r[2])))
      simp(lambda :"x - (x+y) -> -y\n\tx = {}\n\ty = {}".format(l, r[2]))
      return
    # x - (y+x) -> -y
    if r[0] == "+" and l == r[2]:
      work_stack.append((True, count, ("neg", r[1])))
      simp(lambda :"x - (y+x) -> -y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return
    # (x+y) - x -> y
    if l[0] == "+" and l[1] == r:
      work_stack.append((True, count, l[2]))
      simp(lambda :"(x+y) - x -> y\n\tx = {}\n\ty = {}".format(r, l[2]))
      return
    # (x+y) - y -> x
    if l[0] == "+" and l[2] == r:
      work_stack.append((True, count, l[1]))
      simp(lambda :"(x+y) - y -> x\n\tx = {}\n\ty = {}".format(l[1], r))
      return

    # x - (x-y) -> y
    if r[0] == "-" and l == r[1]:
      work_stack.append((True, count, r[2]))
      simp(lambda :"x - (x-y) -> y\n\tx = {}\n\ty = {}".format(l, r[2]))
      return
    # x - (y-x) -> (2*x)-y
    if r[0] == "-" and l == r[2]:
      work_stack.append((True, count, ("-", ("*", TWO, l), r[1])))
      simp(lambda :"x - (y-x) -> (2*x)-y\n\tx = {}\n\ty = {}".format(l, r[1]))
      return
    # (x-y) - x -> -y
    if l[0] == "-" and l[1] == r:
      work_stack.append((True, count, ("neg", l[2])))
      simp(lambda :"(x-y) - x -> -y\n\tx = {}\n\ty = {}".format(r, l[2]))
      return
    # (x-y) - y -> x-(2*y)
    if l[0] == "-" and l[2] == r:
      work_stack.append((True, count, ("-", l[1], ("*", TWO, r))))
      simp(lambda :"(x-y) - y -> x-(2*y)\n\tx = {}\n\ty = {}".format(l[1], r))
      return

    # x - (n*x) -> (n-1)*x
    if r[0] == "*" and l == r[2]:
      simp(lambda :"x - (n*x) -> (n-1)*x\n\tx = {}".format(l))
      if r[1][0] == "Integer":
        work_stack.append((True, count, ("*", ("Integer", str(int(r[1][1])-1)), l)))
        return
      work_stack.append((True, count, ("*", ("-", r[1], ONE), l)))
      return
    # x - (x*n) -> (n-1)*x
    if r[0] == "*" and l == r[1]:
      simp(lambda :"x - (x*n) -> (n-1)*x\n\tx = {}".format(l))
      if r[2][0] == "Integer":
        work_stack.append((True, count, ("*", ("Integer", str(int(r[2][1])-1)), l)))
        return
      work_stack.append((True, count, ("*", ("-", r[2], ONE), l)))
      return
    # (n*x) - x -> (n-1)*x
    if l[0] == "*" and r == l[2]:
      simp(lambda :"(n*x) - x -> (n-1)*x\n\tx = {}".format(r))
      if l[1][0] == "Integer":
        work_stack.append((True, count, ("*", ("Integer", str(int(l[1][1])-1)), r)))
        return
      work_stack.append((True, count, ("*", ("-", l[1], ONE), r)))
      return
    # (x*n) - x -> (n-1)*x
    if l[0] == "*" and r == l[1]:
      simp(lambda :"(x*n) - x -> (n-1)*x\n\tx = {}".format(r))
      if l[2][0] == "Integer":
        work_stack.append((True, count, ("*", ("Integer", str(int(l[2][1])-1)), r)))
        return
      work_stack.append((True, count, ("*", ("-", l[2], ONE), r)))
      return

    work_stack.append((True, count, tuple(args)))


  def _mul(work_stack, count, args):
    assert(args[0] == "*")
    assert(len(args) == 3)
    l, r = args[1], args[2]

    # Collapse integer expressions
    if l[0] == "Integer" and r[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(int(l[1])*int(r[1])))))
      return

    # 1 * x -> x
    if l == ONE:
      work_stack.append((True, count, r))
      simp(lambda :"Eliminated One in multiply")
      return
    # x * 1 -> x
    if r == ONE:
      work_stack.append((True, count, l))
      simp(lambda :"Eliminated One in multiply")
      return

    # (-1) * x -> -x
    if l == NEG_ONE:
      work_stack.append((True, count, ("neg", r)))
      simp(lambda :"Eliminated Negative One in multiply")
      return
    # x * (-1) -> -x
    if r == NEG_ONE:
      work_stack.append((True, count, ("neg", l)))
      simp(lambda :"Eliminated Negative One in multiply")
      return

    # x * x -> x^2
    if r == l:
      work_stack.append((True, count, ("pow", l, TWO)))
      simp(lambda :"x * x -> x^2\n\tx = {}\n".format(r))
      return

    # (x^n) * x -> x^(n+1)
    if l[0] == "pow" and l[1] == r:
      work_stack.append((True, count, ("pow", r, ("Integer", str(int(l[2][1])+1)))))
      simp(lambda :"(x^n) * x -> x^(n+1)\n\tx = {}\n".format(r))
      return
    # x * (x^n) -> x^(n+1)
    if r[0] == "pow" and l == r[1]:
      work_stack.append((True, count, ("pow", l, ("Integer", str(int(r[2][1])+1)))))
      simp(lambda :"x * (x^n) -> x^(n+1)\n\tx = {}\n".format(l))
      return
    # (x^n) * (x^m) -> x^(n+m)
    if r[0] == "pow" and l[0] == "pow" and l[1] == r[1]:
      work_stack.append((True, count, ("pow", l[1], ("Integer", str(int(l[2][1])+int(r[2][1]))))))
      simp(lambda :"(x^n) * (x^m) -> x^(n+m)\n\tx = {}\n".format(l[1]))
      return

    work_stack.append((True, count, tuple(args)))


  def _pow(work_stack, count, args):
    assert(args[0] in {"pow", "powi"})
    assert(len(args) == 3)
    l, r = args[1], args[2]

    # Collapse integer expressions
    if l[0] == "Integer" and r[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(int(l[1])**int(r[1])))))
      return

    # x ^ 1 -> x
    if r == ONE:
      work_stack.append((True, count, l))
      simp(lambda :"Eliminated One in power")
      return

    # abs(x) ^ (2*n) -> x^(2*n)
    if l[0] == "abs" and r[0] == "Integer" and int(r[1])%2==0:
      work_stack.append((True, count, ("pow", l[1], r)))
      simp(lambda :"abs(x) ^ (2*n) -> x^(2*n)\n\tx = {}".format(l[1]))
      return

    # (-x) ^ (2*n) -> x^(2*n)
    if l[0] == "neg" and r[0] == "Integer" and int(r[1])%2==0:
      work_stack.append((True, count, ("pow", l[1], r)))
      simp(lambda :"(-x) ^ (2*n) -> x^(2*n)\n\tx = {}".format(l[1]))
      return

    work_stack.append((True, count, tuple(args)))


  def _neg(work_stack, count, args):
    assert(args[0] == "neg")
    assert(len(args) == 2)
    arg = args[1]

    # Collapse integer expressions
    if arg[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(-int(arg[1])))))
      return

    # -(-x) -> x
    if arg[0] == "neg":
      work_stack.append((True, count, arg[1]))
      simp(lambda :"Eliminated double negative in negative")
      return

    work_stack.append((True, count, tuple(args)))


  def _abs(work_stack, count, args):
    assert(args[0] == "abs")
    assert(len(args) == 2)
    arg = args[1]

    # Collapse integer expressions
    if arg[0] == "Integer":
      work_stack.append((True, count, ("Integer", str(abs(int(arg[1]))))))
      return

    # abs(-x)     -> abs(x)
    # abs(abs(x)) -> abs(x)
    if arg[0] == "neg" or arg[0] == "abs":
      work_stack.append((True, count, ("abs", arg[1])))
      simp(lambda :"Eliminated double abs in abs")
      return

    # abs(x^(2*n)) -> x^2n
    if arg[0] == "pow" and int(arg[2][1])%2 == 0:
      work_stack.append((True, count, arg))
      simp(lambda :"abs(x^(2*n)) -> x^2n\n\tx = {}".format(arg[1]))
      return

    work_stack.append((True, count, tuple(args)))


  def _cos(work_stack, count, args):
    assert(args[0] ==  "cos")
    assert(len(args) == 2)
    arg = args[0]

    # cos(-x) -> cos(x)
    if arg[0] == "neg":
      work_stack.append((True, count, ("cos", arg[1])))
      simp(lambda :"cos(-x) -> cos(x)\n\tx = {}".format(arg[1]))
      return

    work_stack.append((True, count, tuple(args)))


  def _cosh(work_stack, count, args):
    assert(args[0] == "cosh")
    assert(len(args) == 2)
    arg = args[1]

    # cosh(-x) -> cosh(x)
    if arg[0] == "neg":
      work_stack.append((True, count, ("cosh", arg[1])))
      simp(lambda :"cosh(-x) -> cosh(x)\n\tx = {}".format(arg[1]))
      return

    work_stack.append((True, count, ("cosh", arg)))


  def _variable(work_stack, count, args):
    assert(args[0] == "Variable")
    assert(len(args) == 3)
    val = args[2]

    if val[0] in C_OR_V:
      work_stack.append((True, count, val))
      return

    work_stack.append((True, count, tuple(args[0:2])))

  my_contract_dict = {"+":        _add,
                      "-":        _sub,
                      "*":        _mul,
                      "pow":      _pow,
                      "powi":     _pow,
                      "neg":      _neg,
                      "abs":      _abs,
                      "cos":      _cos,
                      "cosh":     _cosh,
                      "Variable": _variable}

  exp = walk(dict(), my_contract_dict, exp, assigns)

  return exp











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
