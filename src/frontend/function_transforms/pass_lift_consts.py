#!/usr/bin/env python3

from pass_manager import *

import collections
import sys


def lift_consts(exp, inputs, assigns, consts=None):
  if consts == None:
    consts = collections.OrderedDict()

  bops = {'+': lambda l,r:str(int(l[1])+int(r[1])),
          '-': lambda l,r:str(int(l[1])-int(r[1])),
          '*': lambda l,r:str(int(l[1])*int(r[1])),}
  uops = {'Neg': lambda a:str(-int(a[1]))}

  def expand(exp):
    if exp[0] in UNOPS:
      return [exp[0], expand(exp[1])]
    if exp[0] in bops:
      l = expand(exp[1])
      r = expand(exp[2])
      if l[0] == "Integer" and r[0] == "Integer":
        return ["Integer", bops[exp[0]](l, r)]
      # purposely fall through
    if exp[0] in uops:
      a = expand(exp[1])
      if a[0] == "Integer":
        return ["Integer", uops[exp[0]](a)]
      # purposely fall through
    if exp[0] in BINOPS:
      return [exp[0], expand(exp[1]), expand(exp[2])]
    if exp[0] in {"Const"}:
      return consts[exp[1]][:]
    if exp[0] in {"Input", "Integer", "Float", "ConstantInterval"}:
      return exp
    print("Internal error in expand")
    sys.exit(-1)

  def make_constant(exp):
    if exp[0] == "Const":
      assert(exp[1] in consts)
      return exp
    exp = expand(exp)
    key = const_hash(exp)
    if key not in consts:
      consts[key] = exp[:]
    return ['Const', key]

  def replace_exp(exp, new_exp):
    for i in range(len(new_exp)):
      try:
        exp[i] = new_exp[i]
      except IndexError:
        exp.append(new_exp[i])
    del exp[len(new_exp):]

  def _lift_consts(exp):
    # First reduce identity functions
    if exp[0] in {"pow"}:
      assert(exp[2][0] == "Integer")
      if exp[2][1] == "1":
        replace_exp(exp, exp[1][:])
        return _lift_consts(exp)
      return _lift_consts(exp[1])

    if exp[0] in {"+"}:
      l = expand(exp[1])
      r = expand(exp[2])
      new_exp = None
      if l[0] == "Integer" and l[1] == "0":
        new_exp = exp[2][:]
      if r[0] == "Integer" and r[1] == "0":
        new_exp = exp[1][:]
      if new_exp:
        replace_exp(exp, new_exp)
        return _lift_consts(exp)
      else:
        # purposely fall through
        pass

    if exp[0] in {"*"}:
      l = expand(exp[1])
      r = expand(exp[2])
      new_exp = None
      if l[0] == "Integer" and l[1] == "1":
        new_exp = exp[2][:]
      if r[0] == "Integer" and r[1] == "1":
        new_exp = exp[1][:]
      if new_exp:
        replace_exp(exp, new_exp)
        return _lift_consts(exp)
      else:
        # purposely fall through
        pass

    if exp[0] in {"Const"}:
      assert(exp[1] in consts)
      return True

    if exp[0] in {"sinh", "cosh", "tanh", "dabs", "datanh"}:
      # Crlibm is claimed to not be ULP accurate by GAOL. Hence, we must defer
      # to implementations based on the exponential function.
      inner = _lift_consts(exp[1])
      if inner:
        make_constant(exp[1])
      return False;

    if exp[0] in {"powi"}:
      e = expand(exp[2])
      if e[0] == "Integer":
        exp[0] = "pow"
        exp[2] = e
        return _lift_consts(exp)
      # purposely fall through

    if exp[0] in UNOPS:
      return _lift_consts(exp[1])

    if exp[0] in BINOPS:
      first  = _lift_consts(exp[1])
      second = _lift_consts(exp[2])
      if first and second:
        return True
      elif first:
        exp[1] = make_constant(exp[1])
      elif second:
        exp[2] = make_constant(exp[2])
      return False

    if exp[0] in {"InputInterval", "Input"}:
      return False

    if exp[0] in {"Assign"}:
      if _lift_consts(exp[2]):
        exp[2] = make_constant(exp[2])
        return True
      return False

    if exp[0] in {"Variable"}:
      assignment = assigns[exp[1]]
      if _lift_consts(assignment):
        exp[0] = "Const"
        exp[1] = make_constant(assignment)[1]
        return True
      return False

    if exp[0] in {"ConstantInterval", "Float", "Integer"}:
      return True

    if exp[0] in {"Return"}:
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      return False

    if exp[0] in {"Tuple"}:
      if _lift_consts(exp[1]):
        exp[1] = make_constant(exp[1])
      if _lift_consts(exp[2]):
        exp[2] = make_constant(exp[2])
      return False

    if exp[0] in {"Box"}:
      all_const = True
      for i in range(1, len(exp)):
        all_const &= _lift_consts(exp[i])
      return all_const

    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)

  for k,v in assigns.items():
    _lift_consts(["Assign", k, v])
  _lift_consts(exp)

  return consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_assigns import lift_assigns

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  assigns = lift_assigns(exp, inputs)
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
