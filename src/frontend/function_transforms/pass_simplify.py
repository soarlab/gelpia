#!/usr/bin/env python3

from pass_utils import *
from pass_lift_consts import lift_consts

import sys


def simplify(exp, inputs, assigns, consts=None):

  def _simplify(exp):
    typ = exp[0]

    if typ in {"pow", "powi"}:
      e = expand(exp[2], assigns, consts)
      if e[0] == "Integer" and e[1] == "1":
        replace_exp(exp, exp[1])
        return True

    if typ == "+":
      l = expand(exp[1], assigns, consts)
      r = expand(exp[2], assigns, consts)
      new_exp = None
      if l[0] == "Integer" and l[1] == "0":
        new_exp = exp[2]
      if r[0] == "Integer" and r[1] == "0":
        new_exp = exp[1]
      if l == r:
        new_r = exp[1] if exp[1][0] == "Variable" else exp[2]
        new_exp = ["*", ["Integer", "2"], new_r]
      if exp[2][0] == "neg":
        new_exp = ["-", exp[1], exp[2][1]]
      if l[0] == "neg" and l[1] == r:
        new_exp = ["Integer", "0"]
      if r[0] == "neg" and r[1] == l:
        new_exp = ["Integer", "0"]
      if new_exp:
        replace_exp(exp, new_exp)
        return True

    if typ == '-':
      l = expand(exp[1], assigns, consts)
      r = expand(exp[2], assigns, consts)
      new_exp = None
      if l[0] == "Integer" and l[1] == "0":
        new_exp = ['neg', exp[2]]
      if r[0] == "Integer" and r[1] == "0":
        new_exp = exp[1]
      if l == r:
        new_exp = ["Integer", "0"]
      if exp[2][0] == "neg":
        new_exp = ["+", exp[1], exp[2][1]]
      if new_exp:
        replace_exp(exp, new_exp)
        return True

    if typ in {"*"}:
      l = expand(exp[1], assigns, consts)
      r = expand(exp[2], assigns, consts)
      new_exp = None
      if l[0] == "Integer" and l[1] == "1":
        new_exp = exp[2]
      if r[0] == "Integer" and r[1] == "1":
        new_exp = exp[1]
      if l[0] == "Integer" and l[1] == "-1":
        new_exp = ["neg", exp[2]]
      if r[0] == "Integer" and r[1] == "-1":
        new_exp = ["neg", exp[1]]
      if r == l:
        b = exp[1] if exp[1][0] == "Variable" else exp[2]
        new_exp = ["pow", b, ["Integer", "2"]]
      if l[0] == "pow" and l[1] == r:
        b = exp[1][1] if exp[1][1][0] == "Variable" else exp[2][1]
        new_exp = ["pow", exp[1][1][:], ["Integer", str(int(exp[1][2][1])+1)]]
      if r[0] == "pow" and r[1] == l:
        b = exp[1][1] if exp[1][1][0] == "Variable" else exp[2][1]
        new_exp = ["pow", exp[2][1][:], ["Integer", str(int(exp[2][2][1])+1)]]
      if r[0] == "pow" and l[0] == "pow" and r[1] ==l[1]:
        b = exp[1][1] if exp[1][1][0] == "Variable" else exp[2][1]
        new_exp = ["pow", exp[1][1][:], ["Integer", str(int(exp[1][2][1])+int(exp[2][2][1]))]]
      if new_exp:
        replace_exp(exp, new_exp)
        return True



    if typ in BINOPS.union({"Tuple"}):
      return _simplify(exp[2]) or _simplify(exp[1])

    if typ in UNOPS.union({"Return"}):
      return _simplify(exp[1])

    if typ == "Variable":
      return  _simplify(assigns[exp[1]])

    if typ == "Box":
      for b in exp[1:]:
        if _simplify(b):
          return True
      return False

    if typ in {"ConstantInterval", "InputInterval", "Float", "Integer",
                  "Const", "Input", "Symbol", "PointInterval"}:
      return False

    print("simplify error unknown: '{}'".format(exp))
    sys.exit(-1)

  while _simplify(exp):
    pass

  if consts != None:
    lift_consts(exp, inputs, assigns, consts)

  return None











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
