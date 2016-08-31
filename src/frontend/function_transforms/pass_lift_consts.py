#!/usr/bin/env python3

from pass_utils import *

import collections
import sys


def lift_consts(exp, inputs, assigns, consts=None):
  if consts == None:
    consts = collections.OrderedDict()


  def make_constant(exp):
    if exp[0] == "Const":
      return exp
    new_exp = expand(exp, assigns, consts)
    key = const_hash(new_exp)
    if key not in consts:
      consts[key] = new_exp[:]
    return ['Const', key]


  CONST = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}

  def _lift_consts(exp):
    tag = exp[0]

    if tag in BINOPS:
      if tag == "powi":
        e = expand(exp[2], assigns, consts)
        if e[0] == "Integer":
          exp[2] = e
          exp[0] = "pow"
      first  = _lift_consts(exp[1])
      second = _lift_consts(exp[2])
      if first and second:
        return True
      elif first:
        exp[1] = make_constant(exp[1])
      elif second:
        exp[2] = make_constant(exp[2])
      return False

    if tag in CONST:
      return True

    if tag == "Input" or tag == "Variable":
      return False

    if tag in UNOPS:
      if tag in {"sinh", "cosh", "tanh", "dabs", "datanh"}:
        # MB: Crlibm is claimed to not be ULP accurate by GAOL. Hence, we must
        # MB: defer to implementations based on the exponential function.
        if _lift_consts(exp[1]):
          exp[1] = make_constant(exp[1])
        return False;
      return _lift_consts(exp[1])

    if tag == "Return":
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      return False

    if tag == "Tuple":
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      if _lift_consts(exp[2]):
        exp[2] = make_constant(exp[2])
      return False

    if tag == "Box":
      for i in range(1, len(exp)):
        if _lift_consts(exp[i]):
          exp[i] = make_constant(exp[i])
      return False

    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)

  for var,val in assigns.items():
    if _lift_consts(val):
      assigns[var] = make_constant(val)
  _lift_consts(exp)

  return consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)

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
