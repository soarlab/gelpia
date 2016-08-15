#!/usr/bin/env python3

from pass_utils import *

import sys


def to_interp(exp, inputs, assigns, consts):
  input_names = [name for name in inputs]
  const_names = [name for name in consts]

  def _to_interp(exp):
    typ = exp[0]

    if typ in {"pow"}:
      e = expand(exp[2], assigns, consts)
      assert(e[0] == "Integer")
      return _to_interp(exp[1]) + ["p"+e[1]]

    if typ in {"powi"}:
      return _to_interp(exp[1]) + _to_interp(exp[2]) + ['op']

    if typ in INFIX:
      return _to_interp(exp[1]) + _to_interp(exp[2]) + ['o'+exp[0]]

    if typ in UNOPS:
      return _to_interp(exp[1]) + ['f'+exp[0].lower()]

    if typ in {"Const"}:
      return ['c'+str(const_names.index(exp[1]))]

    if typ in {"Input"}:
      return ['i'+str(input_names.index(exp[1]))]

    if typ in {"Variable"}:
      return _to_interp(assigns[exp[1]])

    if typ in {"Return"}:
      return _to_interp(exp[1])

    print("to_interp error unknown: '{}'".format(exp))
    sys.exit(-1)


  return ','.join(_to_interp(exp))








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
  consts = lift_consts(exp, inputs, assigns, consts)

  function = to_interp(exp, inputs, assigns, consts)

  print("function:")
  print(function)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)

if __name__ == '__main__':
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
