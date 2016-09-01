#!/usr/bin/env python3

from pass_utils import *

import collections
import re
import sys
import subprocess
import os.path as path


def single_assignment(exp, inputs, assigns, consts=None):
  PASSTHROUGH = {"Integer", "Float", "Input", "Const", "ConstantInterval",
                 "PointInterval"}
  UNCACHED    = PASSTHROUGH.union({"Tuple", "Variable"})
  TWO_ITEMS   = BINOPS.union({"Tuple"})
  ONE_ITEM    = UNOPS.union({"Return"})


  def cache(exp, hashed=dict()):
    if exp[0] in UNCACHED:
      return exp
    try:
      key = hashed[exp]
    except KeyError:
      key = "_expr_"+str(len(hashed))
      hashed[exp] = key
      assigns[key] = exp
    return ("Variable", key)


  def _single_assignment(exp):
    tag = exp[0]

    if tag in PASSTHROUGH:
      return exp

    if tag in TWO_ITEMS:
      left  = _single_assignment(exp[1])
      left  = cache(left)
      right = _single_assignment(exp[2])
      right = cache(right)
      return (exp[0], left, right)

    if tag in ONE_ITEM:
      arg = _single_assignment(exp[1])
      arg = cache(arg)
      return (exp[0], arg)

    if tag == "Variable":
      _single_assignment(assigns[exp[1]])
      return exp

    if tag == "Box":
      rest = list()
      for i in range(1, len(exp)):
        part = _single_assignment(exp[i])
        part = cache(part)
        rest.append(part)
      return ("Box",) + tuple(rest)

    print("single_assignment error unknown: '{}'".format(exp))
    sys.exit(-1)

  result = _single_assignment(exp)

  return result








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_simplify import simplify

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  exp, consts = lift_consts(exp, inputs, assigns)
  exp = simplify(exp, inputs, assigns, consts)
  exp = consts = lift_consts(exp, inputs, assigns, consts)

  exp = single_assignment(exp, inputs, assigns, consts)

  print("function:")
  print()
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
