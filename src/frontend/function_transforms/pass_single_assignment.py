#!/usr/bin/env python3

from pass_utils import *
from expression_walker import walk

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


  def _two_items(work_stack, count, args):
    assert(len(args) == 3)
    left  = cache(args[1])
    right = cache(args[2])
    work_stack.append((True, count, tuple(args)))

  def _one_item(work_stack, count, args):
    assert(len(args) == 2)
    arg = cache(args[1])
    work_stack.append((True, count, tuple(args)))

  def _many_items(work_stack, count, args):
    args = [args[0]] + [cache(sub) for sub in args[1:]]
    work_stack.append((True, count, tuple(args)))

  my_contract_dict = dict()
  my_contract_dict.update(zip(BINOPS, [_two_items for _ in BINOPS]))
  my_contract_dict.update(zip(UNOPS, [_one_item for _ in UNOPS]))
  my_contract_dict["Tuple"] = _two_items
  my_contract_dict["Box"] = _many_items

  exp = walk(dict(), my_contract_dict, exp, assigns)

  return exp








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
