#!/usr/bin/env python3

from pass_utils import *

import sys


def flatten(exp, inputs, assigns, consts, human_readable_p=False):
  lp = ['(']
  rp = [')']
  cm = [',']
  lb = ['[']
  rb = [']']
  nl = ['\n']
  co = [': ']

  def _flatten(exp):
    tag = exp[0]

    if tag in INFIX:
      return lp + _flatten(exp[1]) + [exp[0]] + _flatten(exp[2]) + rp

    if tag in BINOPS:
      return [exp[0]] + lp + _flatten(exp[1]) + cm + _flatten(exp[2]) + rp

    if tag in UNOPS:
      head = exp[0]
      if head == "neg":
        head = "-"
      return [head] + lp + _flatten(exp[1]) + rp

    if tag in {"Integer", "Float"}:
      if human_readable_p:
        if tag == "Float":
          return [str(float(exp[1]))]
        return [exp[1]]
      return lb + [exp[1]] + rb

    if tag in {"InputInterval", "ConstantInterval"}:
      inside = _flatten(exp[1]) + cm + _flatten(exp[2])
      inside = [part for part in inside if part[0] not in  {'[', ']'}]
      return lb + inside + rb

    if tag == "Const":
      return _flatten(consts[exp[1]])

    if tag == "Input":
      if human_readable_p:
        return [exp[1]]
      return _flatten(inputs[exp[1]])

    if tag == "Variable":
      return _flatten(assigns[exp[1]])

    if tag in {"Return", "PointInterval"}:
      return _flatten(exp[1])

    if human_readable_p:
      if tag == "Box":
        inputs_list = list(inputs)
        maxlen = max([0]+[len(i) for i in inputs_list])
        ret = list()
        for var, ex in zip(inputs, exp[1:]):
          var = " "*(maxlen-len(var))+var
          ret += ["    "] + [var] + co + _flatten(ex) + nl
        return ret

      if tag == "Tuple":
        return (["Original: "] + _flatten(exp[1]) + nl +
                ["  Derivatives:"] + nl + _flatten(exp[2]))

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
