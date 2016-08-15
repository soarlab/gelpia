#!/usr/bin/env python3

from pass_utils import *
from pass_lift_consts import lift_consts

import collections
import re
import sys
import subprocess
import os.path as path
import math

def reverse_diff(exp, inputs, assigns, consts=None):
  gradient = collections.OrderedDict([(k,["Integer","0"][:]) for k in inputs])

  def _reverse_diff(exp, adjoint):
    tag = exp[0]

    if tag in {"Input"}:
      old = gradient[exp[1]]
      gradient[exp[1]] =["+", old, adjoint]
      return

    if tag in {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}:
      return

    if tag in {'+'}:
       _reverse_diff(exp[1], adjoint)
       _reverse_diff(exp[2], adjoint)
       return

    if tag in {'-'}:
      _reverse_diff(exp[1], adjoint)
      _reverse_diff(exp[2], ["neg", adjoint])
      return

    if tag in {'*'}:
      left = exp[1]
      right = exp[2]
      _reverse_diff(exp[1], ["*", adjoint, right])
      _reverse_diff(exp[2], ["*", adjoint, left])
      return

    if tag in {'/'}:
      upper = exp[1]
      lower = exp[2]
      _reverse_diff(exp[1], ["/", adjoint, lower])
      _reverse_diff(exp[2], ["/", ["*", ["neg", adjoint], upper], ["pow", lower, ["Integer", "2"]]])
      return

    if tag in {"exp"}:
      expo = exp[1]
      _reverse_diff(exp[1], ["*", ["exp", expo], adjoint])
      return

    if tag in {"log"}:
      base = exp[1]
      _reverse_diff(exp[1], ["/", adjoint, base])
      return

    if tag in {"pow", "powi"}:
      base = exp[1]
      expo = exp[2]
      _reverse_diff(exp[1], ['*', adjoint, ['*', expo, ['powi', base, ['-', expo, ['Integer', "1"]]]]])
      _reverse_diff(exp[2], ['*', adjoint, ['*', ['log', base], ['powi', base, expo]]])
      return

    if tag == "sqrt":
      _reverse_diff(exp[1], ['/', adjoint, ['*', ['Integer', '2'],  ['sqrt', exp[1]]]])
      return

    if tag == "cos":
      _reverse_diff(exp[1], ['*', ["neg", ["sin", exp[1]]], adjoint])
      return

    if tag == "sin":
      _reverse_diff(exp[1], ['*', ["cos", exp[1]], adjoint])
      return

    if tag == "tan":
      _reverse_diff(exp[1], ['*', ['+', ["Integer", "1"], ["pow", ["tan", exp[1]], ["Integer", "2"]]], adjoint])
      return

    if tag == "cosh":
      _reverse_diff(exp[1], ['*', ['sinh', exp[1]], adjoint])
      return

    if tag == "sinh":
      _reverse_diff(exp[1], ['*', ['cosh', exp[1]], adjoint])
      return

    if tag == "tanh":
      _reverse_diff(exp[1], ['*', ['-', ["Integer", "1"], ["pow", ["tanh", exp[1]], ["Integer", "2"]]], adjoint])
      return

    if tag == "abs":
      _reverse_diff(exp[1], ['*', ["dabs", exp[1]], adjoint])
      return

    if tag =="neg":
      _reverse_diff(exp[1], ["neg", adjoint])
      return

    if tag == "Variable":
      _reverse_diff(assigns[exp[1]], adjoint)
      return

    if tag == "Return":
      _reverse_diff(exp[1], adjoint)
      return

    if tag in {"Integer", "Float"}:
      return

    print("reverse_diff error unknown: '{}'".format(exp))
    sys.exit(-1)


  _reverse_diff(exp, ["Integer", "1"])
  result = ["Box"]+[d for d in gradient.values()]
  retval = ["Return", ["Tuple", exp[1], result]]

  return retval








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_dead_removal import dead_removal
  from pass_simplify import simplify
  from output_rust import to_rust
  from pass_single_assignment import single_assignment

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)
  dead_removal(exp, inputs, assigns, consts)

  exp = reverse_diff(exp, inputs, assigns, consts)
  simplify(exp, inputs, assigns, consts)

  if len(sys.argv) == 3 and sys.argv[2] == "test":
    assert(exp[0] == "Return")
    tup = exp[1]
    assert(tup[0] == "Tuple")
    box = tup[2]
    if box[0] == "Const":
      const = box
      assert(const[0] == "Const")
      box = expand(const, assigns, consts)

    assert(box[0] == "Box")
    if len(box) == 1:
      print("No input variables")
      assert(len(inputs) == 0)
      return

    for name, diff in zip(inputs.keys(), box[1:]):
        print("d{} = {}".format(name, expand(diff, assigns, consts)))

  else:
    single_assignment(exp, inputs, assigns, consts)
    print("reverse_diff:")
    print_exp(exp)
    print()
    print_inputs(inputs)
    print()
    print_consts(consts)
    print()
    print_assigns(assigns)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
