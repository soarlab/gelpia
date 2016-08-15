#!/usr/bin/env python3

from pass_utils import *

import collections
import sys


def lift_consts(exp, inputs, assigns, consts=None):
  if consts == None:
    consts = collections.OrderedDict()

  def make_constant(exp):
    if exp[0] == "Const":
      assert(exp[1] in consts)
      return exp
    exp = expand(exp, assigns, consts)
    key = const_hash(exp)
    if key not in consts:
      consts[key] = exp[:]
    return ['Const', key]

  def _lift_consts(exp):
    typ = exp[0]

    if typ in {"Const"}:
      assert(exp[1] in consts)
      return True

    if typ in {"sinh", "cosh", "tanh", "dabs", "datanh"}:
      # MB: Crlibm is claimed to not be ULP accurate by GAOL. Hence, we must
      # MB: defer to implementations based on the exponential function.
      inner = _lift_consts(exp[1])
      if inner:
        make_constant(exp[1])
      return False;

    if typ in {"powi"}:
      e = expand(exp[2], assigns, consts)
      if e[0] == "Integer":
        exp[0] = "pow"
        exp[2] = e
        return _lift_consts(exp)
      else:
        # purposely fall through
        pass

    if typ in UNOPS:
      return _lift_consts(exp[1])

    if typ in BINOPS:
      first  = _lift_consts(exp[1])
      second = _lift_consts(exp[2])
      if first and second:
        return True
      elif first:
        exp[1] = make_constant(exp[1])
      elif second:
        exp[2] = make_constant(exp[2])
      return False

    if typ in {"InputInterval", "Input"}:
      return False

    if typ in {"Variable"}:
      assignment = assigns[exp[1]]
      if _lift_consts(assignment):
        new_exp = make_constant(assignment)
        replace_exp(exp, new_exp)
        return True
      return False

    if typ in {"ConstantInterval", "PointInterval", "Float", "Integer"}:
      return True

    if typ in {"Return"}:
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      return False

    if typ in {"Tuple"}:
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      if _lift_consts(exp[2]):
        exp[2] = make_constant(exp[2])
      return False

    if typ in {"Box"}:
      all_const = True
      for i in range(1, len(exp)):
        all_const &= _lift_consts(exp[i])
      return all_const

    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)

  _lift_consts(exp)

  return consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)

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
