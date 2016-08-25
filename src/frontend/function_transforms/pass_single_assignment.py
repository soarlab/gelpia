#!/usr/bin/env python3

from pass_utils import *

import collections
import re
import sys
import subprocess
import os.path as path


def single_assignment(exp, inputs, assigns, consts):

  def cache(exp):
    if exp[0] in {"Integer", "Float", "InputInterval",
                  "PointInterval", "Input", "Const", "Tuple"}:
      return exp
    if exp[0] == "Variable":
      assert(exp[1] in assigns)
      return exp
    key = cache_hash(exp)
    if key not in assigns:
      assigns[key] = exp[:]
    return ["Variable", key]

  def search_replace(var, val, exp):
    def _search_replace(exp):
      if type(exp) is not list or len(exp) < 1:
        return
      if exp[0] == "Variable" and exp[1] == var:
        replace_exp(exp, val)
        return
      for e in exp[1:]:
        _search_replace(e)

    if str(var) in str(exp):
      _search_replace(exp)
    return

  def collapse(exp):
    assert(exp[0] == "Return")
    retval = exp[1]
    boxvars = ""
    if retval[0] == "Tuple":
      boxvars = str(assigns[retval[2][1]])
    usages = "\n".join([str(k) for k in assigns.values()]) + str(retval)
    single_used = dict()
    for var in assigns:
      if usages.count(var) == 1 and boxvars.count(var) == 0:
        single_used[var] = assigns[var]
    for var in single_used:
      del assigns[var]
      for val in assigns.values():
        search_replace(var, single_used[var], val)
      search_replace(var, single_used[var], exp)

  def _single_assignment(exp):
    typ = exp[0]

    if typ in {"Input", "InputInterval", "Const", "Integer", "Float", "Const"}:
      return exp

    if typ in BINOPS:
      left = cache(_single_assignment(exp[1]))
      right = cache(_single_assignment(exp[2]))
      return [typ, left, right]

    if typ in UNOPS:
      arg = cache(_single_assignment(exp[1]))
      return [typ, arg]

    if typ == "Variable":
      _single_assignment(assigns[exp[1]])
      return exp

    if typ == "Return":
      ret = cache(_single_assignment(exp[1]))
      return ["Return", ret]

    if typ =="Tuple":
      exp[1] = cache(_single_assignment(exp[1]))
      exp[2] = cache(_single_assignment(exp[2]))
      return exp

    if typ == "Box":
      for i in range(1, len(exp)):
        exp[i] = cache(_single_assignment(exp[i]))
      return exp

    print("single_assignment error unknown: '{}'".format(exp))
    sys.exit(-1)

  result = _single_assignment(exp)
  # to be reinabled at a later date
  # collapse(result)

  return result








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
