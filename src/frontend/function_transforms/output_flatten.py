#!/usr/bin/env python3

from pass_utils import *

import sys


def flatten(exp, inputs, assigns, consts):
  lp = ['(']
  rp = [')']
  cm = [',']
  lb = ['[']
  rb = [']']

  def _flatten(exp):
    typ = exp[0]

    if typ in INFIX:
      return lp + _flatten(exp[1]) + [exp[0]] + _flatten(exp[2]) + rp

    if typ in BINOPS:
      return [exp[0]] + lp + _flatten(exp[1]) + cm + _flatten(exp[2]) + rp

    if typ in UNOPS:
      return [exp[0]] + lp + _flatten(exp[1]) + rp

    if typ in {"Integer", "Float"}:
      return lb + [exp[1]] + rb

    if typ in {"InputInterval", "ConstantInterval"}:
      inside = _flatten(exp[1]) + cm + _flatten(exp[2])
      inside = [part for part in inside if part[0] not in  {'[', ']'}]
      return lb + inside + rb

    if typ == "Const":
      return _flatten(consts[exp[1]])

    if typ == "Input":
      return _flatten(inputs[exp[1]])

    if typ == "Variable":
      return _flatten(assigns[exp[1]])

    if typ in {"Return", "PointInterval"}:
      return _flatten(exp[1])

    print("flatten error unknown: '{}'".format(exp))
    sys.exit(-1)


  return ''.join(_flatten(exp))








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

  flattened = flatten(exp, inputs, assigns, consts)

  print("flattened:")
  print(flattened)
  print()
  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
