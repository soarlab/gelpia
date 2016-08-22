#!/usr/bin/env python3

from pass_utils import *

import sys


def dead_removal(exp, inputs, assigns, consts=None):
  used_inputs = set()
  used_assigns = set()
  used_consts = set()

  def _dead_removal(exp):
    if type(exp) is not list:
      return
    tag = exp[0]

    if tag == "Const":
      assert(exp[1] in consts)
      used_consts.add(exp[1])
      return

    if tag == "Variable":
      assert(exp[1] in assigns)
      used_assigns.add(exp[1])
      _dead_removal(assigns[exp[1]])
      return

    if tag == "Input":
      assert(exp[1] in inputs)
      used_inputs.add(exp[1])
      return

    if tag in BINOPS.union(UNOPS).union({"Return", "ConstantInterval",
                                         "PointInterval", "Float", "Integer",
                                         "Box", "Tuple"}):
      for e in exp[1:]:
        _dead_removal(e)
      return

    print("Error unknown in dead_removal: '{}'".format(exp))
    sys.exit(-1)

  _dead_removal(exp)

  for k in list(inputs):
    if k not in used_inputs:
      del inputs[k]

  for k in list(assigns):
    if k not in used_assigns:
      del assigns[k]

  if consts:
    for k in list(consts):
      if k not in used_consts:
        del consts[k]

  return








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_simplify import simplify

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)
  simplify(exp, inputs, assigns, consts)

  dead_removal(exp, inputs, assigns, consts)

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
