#!/usr/bin/env python3

from pass_manager import *

import collections
import sys


def lift_assign(exp, inputs, consts):
  assign = collections.OrderedDict()
  
  def _lift_assign(exp):
    if type(exp[0]) is list:
      assig = exp[0]
      name = assig[1]
      val = assig[2]
      assign[name[1]] = val
      exp[0] = exp[1][0]
      exp[1] = exp[1][1]
      _lift_assign(exp)
      return

    if exp[0] in {"Return"}:
      return

    print("lift_assigns error unknown: '{}'".format(exp))
    sys.exit(-1)

  _lift_assign(exp)
  return assign








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_consts import lift_consts
  
  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  consts = lift_consts(exp, inputs)
  assign = lift_assign(exp, inputs, consts)
  
  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)
  print()
  print_assign(assign)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
