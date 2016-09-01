#!/usr/bin/env python3

from pass_utils import *

import sys


def dead_removal(exp, inputs, assigns, consts=None):
  used_inputs = set()
  used_assigns = set()
  used_consts = set()


  TWO_ITEMS = BINOPS.union({"Tuple"})
  ONE_ITEM  = UNOPS.union({"Return"})
  UNUSED = {"ConstantInterval", "PointInterval", "Float", "Integer"}

  def _dead_removal(exp):
    tag = exp[0]

    if tag == "Variable":
      if exp[1] not in used_assigns:
        used_assigns.add(exp[1])
        _dead_removal(assigns[exp[1]])
      return

    if tag in TWO_ITEMS:
      _dead_removal(exp[1])
      _dead_removal(exp[2])
      return

    if tag == "Const":
      used_consts.add(exp[1])
      return

    if tag == "Input":
      used_inputs.add(exp[1])
      return

    if tag in ONE_ITEM:
      _dead_removal(exp[1])
      return

    if tag in UNUSED:
      return

    if tag == "Box":
      for e in exp[1:]:
        _dead_removal(e)
      return

    print("Error unknown in dead_removal: '{}'".format(exp))
    sys.exit(-1)

  _dead_removal(exp)

  dead_inputs = set(inputs).difference(used_inputs)
  for k in dead_inputs:
    del inputs[k]

  dead_assigns = set(assigns).difference(used_assigns)
  for k in dead_assigns:
    del assigns[k]

  if consts:
    dead_consts = set(consts).difference(used_consts)
    for k in dead_consts:
        del consts[k]

  return








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_simplify import simplify

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  exp, consts = lift_consts(exp, inputs, assigns)
  exp = simplify(exp, inputs, assigns, consts)

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
