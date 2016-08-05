#!/usr/bin/env python3

from pass_manager import *

import collections
import sys


def lift_assigns(exp, inputs):
  assigns = collections.OrderedDict()

  def _lift_assigns(exp):
    if type(exp[0]) is list:
      assig = exp[0]
      name = assig[1]
      val = assig[2]
      assigns[name[1]] = val
      exp[0] = exp[1][0]
      exp[1] = exp[1][1]
      _lift_assigns(val)
      _lift_assigns(exp)
      return

    if exp[0] in UNOPS:
      _lift_assigns(exp[1])
      return

    if exp[0] in BINOPS:
      _lift_assigns(exp[1])
      _lift_assigns(exp[2])
      return

    if exp[0] in {"Input", "Integer", "Float", "Variable", "ConstantInterval"}:
      return

    if exp[0] in {"Name"}:
      if exp[1] in assigns:
        exp[0] = "Variable"
        return
      else:
        print("Error variable name used which was not defined: {}".format(exp[1]))
        sys.exit(-1)

    if exp[0] in {"Return"}:
      _lift_assigns(exp[1])
      return

    print("lift_assigns error unknown: '{}'".format(exp))
    sys.exit(-1)

  _lift_assigns(exp)
  return assigns








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  assigns = lift_assigns(exp, inputs)

  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_assigns(assigns)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
