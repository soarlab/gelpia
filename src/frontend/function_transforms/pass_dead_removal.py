#!/usr/bin/env python3

from pass_utils import *
from expression_walker import no_mut_walk

import collections
import sys


def dead_removal(exp, inputs, assigns, consts=None):
  used_inputs = set()
  used_assigns = set()
  used_consts = set()


  def _variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 2)
    assert(exp[1] in assigns)
    if exp[1] not in used_assigns:
      used_assigns.add(exp[1])
      work_stack.append((False, 2,     assigns[exp[1]]))

  def _input(work_stack, count, exp):
    assert(exp[0] == "Input")
    assert(len(exp) == 2)
    assert(exp[1] in inputs)
    used_inputs.add(exp[1])

  def _const(work_stack, count, exp):
    assert(exp[0] == "Const")
    assert(len(exp) == 2)
    assert(exp[1] in consts)
    used_consts.add(exp[1])


  my_expand_dict = {"Variable": _variable,
                    "Input": _input,
                    "Const": _const}

  no_mut_walk(my_expand_dict, exp, assigns)

  new_inputs = collections.OrderedDict()
  for k in inputs:
    if k in used_inputs:
      new_inputs[k] = inputs[k]

  new_assigns = collections.OrderedDict()
  for k in assigns:
    if k in used_assigns:
      new_assigns[k] = assigns[k]

  if consts == None:
    return new_inputs, new_assigns

  new_consts = collections.OrderedDict()
  for k in consts:
    if k in used_consts:
      new_consts[k] = consts[k]

  return new_inputs, new_assigns, new_consts









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
