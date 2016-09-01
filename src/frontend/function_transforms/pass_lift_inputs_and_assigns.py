#!/usr/bin/env python3

from pass_utils import *

import collections
import sys
import subprocess
import os.path as path


def lift_inputs_and_assigns(exp):
  """Extracts input variables and assignments from an expression """
  assigns = collections.OrderedDict()
  inputs  = collections.OrderedDict()
  implicit_input_count = 0


  def _lift_inputs_and_assigns(exp):
    nonlocal implicit_input_count
    tag = exp[0]

    if type(tag) is tuple:
      assignment = exp[0]
      name = assignment[1]
      val  = assignment[2]
      if val[0] == "InputInterval":
        inputs[name[1]] = val
      else:
        assigns[name[1]] = _lift_inputs_and_assigns(val)
      return  _lift_inputs_and_assigns(exp[1])

    if tag in BINOPS:
      l = _lift_inputs_and_assigns(exp[1])
      r = _lift_inputs_and_assigns(exp[2])
      return (exp[0], l, r)

    if tag in UNOPS.union({"Return"}):
      arg = _lift_inputs_and_assigns(exp[1])
      return (exp[0], arg)

    if tag in {"ConstantInterval", "PointInterval", "Float", "Integer", "Input",
               "Variable"}:
      return exp

    if tag == "InputInterval":
      interval = exp[:]
      name = "$Implicit_Input_{}".format(implicit_input_count)
      new_exp = ("Input", name)
      implicit_input_count += 1
      inputs[name] = interval
      return new_exp

    if tag == "Name":
      typ = None
      if exp[1] in inputs:
        typ = "Input"
      elif exp[1] in assigns:
        typ = "Variable"
      else:
        print("Use of undeclared name: {}".format(exp[1]))
        sys.exit(-1)
      return (typ, exp[1])

    print("lift_inputs_and_assigns error unknown: '{}'".format(exp))
    sys.exit(-1)


  new_exp = _lift_inputs_and_assigns(exp)

  return new_exp, inputs, assigns








def runmain():
  from lexed_to_parsed import parse_function

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)

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
