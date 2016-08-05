#!/usr/bin/env python3

from pass_manager import *

import collections
import re
import sys
import subprocess
import os.path as path


def single_assignment(exp, inputs, assigns, consts, name_cache=list()):

  def cache(exp):
    if exp[0] in {"Integer", "Float", "Variable", "InputInterval", "Input", "Const"}:
      return exp
    key = cache_hash(exp)
    if key not in assigns:
      assigns[key] = exp[:]
    return ["Variable", key]

  def _single_assignment(exp):
    if exp[0] in {"Input", "InputInterval", "Const", "Integer", "Float", "Const"}:
      return exp
    if exp[0] in BINOPS:
      left = cache(_single_assignment(exp[1]))
      right = cache(_single_assignment(exp[2]))
      return [exp[0], left, right]
    if exp[0] in UNOPS:
      arg = cache(_single_assignment(exp[1]))
      return [exp[0], arg]
    if exp[0] in {"Variable"}:
      _single_assignment(assigns[exp[1]])
      return exp
    if exp[0] in {"Return"}:
      ret = cache(_single_assignment(exp[1]))
      return ret
    if exp[0] in {"Tuple"}:
      exp[1] = cache(_single_assignment(exp[1]))
      exp[2] = cache(_single_assignment(exp[2]))
      return exp
    if exp[0] in {"Box"}:
      for i in range(1, len(exp)):
        exp[i] = cache(_single_assignment(exp[i]))
      return exp

    print("single_assignment error unknown: '{}'".format(exp))
    sys.exit(-1)

  result = _single_assignment(exp)
  return result








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_consts import lift_consts
  from pass_lift_assigns import lift_assigns
  from pass_pow import pow_replacement

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  assigns = lift_assigns(exp, inputs)
  consts = lift_consts(exp, inputs, assigns)
  pow_replacement(exp, inputs, assigns, consts)

  exp = single_assignment(exp, inputs, assigns, consts)
  consts = lift_consts(exp, inputs, assigns, consts)

  print("single_assignment:")
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
