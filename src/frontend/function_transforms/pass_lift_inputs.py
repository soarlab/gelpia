#!/usr/bin/env python3

from pass_manager import *

import collections
import sys
import subprocess
import os.path as path

def lift_inputs(exp):
  inputs = collections.OrderedDict()
  used_inputs = set()
  implicit_input_count = 0

  def _lift_inputs(exp):
    nonlocal implicit_input_count

    if type(exp[0]) is list:
      assigns = exp[0]
      name = assigns[1]
      val = assigns[2]
      if val[0] == "InputInterval":
        inputs[name[1]] = val
        exp[0] = exp[1][0]
        exp[1] = exp[1][1]
        _lift_inputs(exp)
      else:
        _lift_inputs(exp[0])
        _lift_inputs(exp[1])
      return

    if exp[0] in BINOPS:
      _lift_inputs(exp[1])
      _lift_inputs(exp[2])
      return

    if exp[0] in UNOPS.union({"Return"}):
      _lift_inputs(exp[1])
      return

    if exp[0] in {"ConstantInterval", "Float", "Integer", "Symbol"}:
      return

    if exp[0] == "InputInterval":
      interval = exp[:]
      exp[0] = "Input"
      exp[1] = "$Implicit_Input_{}".format(implicit_input_count)
      used_inputs.add(exp[1])
      implicit_input_count += 1
      del exp[2:]
      inputs[exp[1]] = interval
      return

    if exp[0] == "Name":
      if exp[1] in inputs:
        used_inputs.add(exp[1])
        exp[0] = "Input"
      return

    if exp[0] == "Assign":
      _lift_inputs(exp[2])
      return

    print("lift_inputs error unknown: '{}'".format(exp))
    sys.exit(-1)


  _lift_inputs(exp)

  for k in list(inputs):
    if k not in used_inputs:
      del inputs[k]

  return inputs








def runmain():
  from lexed_to_parsed import parse_function

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)

  print_exp(exp)
  print()
  print_inputs(inputs)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
