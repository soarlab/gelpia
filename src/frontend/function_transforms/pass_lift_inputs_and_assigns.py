#!/usr/bin/env python3

from pass_utils import *

import collections
import sys
import subprocess
import os.path as path


def lift_inputs_and_assigns(exp):
  """Extracts input variables and assignmentsfrom an expression """
  assigns = collections.OrderedDict()
  inputs = collections.OrderedDict()
  implicit_input_count = 0

  def _lift_inputs_and_assigns(exp):
    nonlocal implicit_input_count
    typ = exp[0]
    if type(typ) is list:
      assignment = exp[0]
      assert(assignment[0] == "Assign")
      name = assignment[1]
      val = assignment[2]
      if val[0] == "InputInterval":
        inputs[name[1]] = val
      else:
        assigns[name[1]] = val
        _lift_inputs_and_assigns(val)
      replace_exp(exp, exp[1])
      _lift_inputs_and_assigns(exp)
      return

    if typ in BINOPS:
      _lift_inputs_and_assigns(exp[1])
      _lift_inputs_and_assigns(exp[2])
      return

    if typ in UNOPS.union({"Return"}):
      _lift_inputs_and_assigns(exp[1])
      return

    if typ in {"ConstantInterval", "PointInterval", "Float", "Integer", "Input",
               "Variable"}:
      return

    if typ == "InputInterval":
      interval = exp[:]
      new_exp = ["Input", "$Implicit_Input_{}".format(implicit_input_count)]
      replace_exp(exp, new_exp)
      used_inputs.add(exp[1])
      implicit_input_count += 1
      inputs[exp[1]] = interval
      return

    if exp[0] == "Name":
      if exp[1] in inputs:
        exp[0] = "Input"
      elif exp[1] in assigns:
        exp[0] = "Variable"
      else:
        print("Use of undeclared name: {}".format(exp[1]))
        sys.exit(-1)
      return

    print("lift_inputs_and_assigns error unknown: '{}'".format(exp))
    sys.exit(-1)


  _lift_inputs_and_assigns(exp)

  return inputs, assigns








def runmain():
  from lexed_to_parsed import parse_function

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)

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
