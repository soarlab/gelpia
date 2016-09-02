#!/usr/bin/env python3

from pass_utils import *

import collections
import sys


def lift_consts(exp, inputs, assigns, consts=None, hashed=dict()):
  if consts == None:
    consts = collections.OrderedDict()


  def make_constant(exp):
    if exp[0] == "Const":
      return exp
    new_exp = expand(exp, assigns, consts)
    try:
      key = hashed[new_exp]
    except KeyError:
      key = "_const_"+str(len(hashed))
      hashed[new_exp] = key
      consts[key] = new_exp
    return ('Const', key)


  CONST = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}

  def _lift_consts(exp):
    tag = exp[0]

    if tag in BINOPS:
      if tag == "powi":
        e = expand(exp[2], assigns, consts)
        if e[0] == "Integer":
          f, first = _lift_consts(exp[1])
          if f:
            return True, ("pow", first, e)
          return False, ("pow", first, e)

      f, first  = _lift_consts(exp[1])
      s, second = _lift_consts(exp[2])
      if f and s:
        return True, (exp[0], first, second)
      elif f:
        first = make_constant(exp[1])
      elif s:
        second = make_constant(exp[2])
      return False, (exp[0], first, second)

    if tag in CONST:
      return True, exp

    if tag == "Input" or tag == "Variable":
      return False, exp

    if tag in UNOPS:
      if tag in {"sinh", "cosh", "tanh", "dabs", "datanh"}:
        # MB: Crlibm is claimed to not be ULP accurate by GAOL. Hence, we must
        # MB: defer to implementations based on the exponential function.
        a, arg = _lift_consts(exp[1])
        if a:
          arg = make_constant(exp[1])
        return False, (exp[0], arg)
      a, arg = _lift_consts(exp[1])
      return a, (exp[0], arg)

    if tag == "Return":
      n, new_exp = _lift_consts(exp[1])
      if n:
        new_exp = make_constant(exp[1])
      return False, ("Return", new_exp)

    if tag == "Tuple":
      f, first  = _lift_consts(exp[1])
      s, second = _lift_consts(exp[2])
      if f:
        first = make_constant(exp[1])
      if s:
        second = make_constant(exp[2])
      return False, ("Tuple", first, second)

    if tag == "Box":
      rest = list()
      for i in range(1, len(exp)):
        p, part = _lift_consts(exp[i])
        if p:
          part = make_constant(exp[i])
        rest.append(part)
      return False, ("Box",)+tuple(rest)

    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)

  for var,val in assigns.items():
    n, new_exp = _lift_consts(val)
    if n:
      assigns[var] = make_constant(new_exp)
    else:
      assigns[var] = new_exp

  _, new_exp = _lift_consts(exp)

  return new_exp, consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  exp, consts = lift_consts(exp, inputs, assigns)

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
