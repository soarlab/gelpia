#!/usr/bin/env python3

from pass_manager import *

import collections
import re
import sys
import subprocess
import os.path as path
import math

def reverse_diff(exp, inputs, assigns, consts):
  gradient = collections.OrderedDict([(k,None) for k in inputs])

  def _reverse_diff(exp, adjoint):
    if exp[0] in {"Input"}:
      if gradient[exp[1]] == None:
        gradient[exp[1]] = adjoint
        return
      old = gradient[exp[1]]
      gradient[exp[1]] =["+", old, adjoint]
      return

    if exp[0] in {"Const"}:
      return

    if exp[0] in {'+'}:
       _reverse_diff(exp[1], adjoint)
       _reverse_diff(exp[2], adjoint)
       return

    if exp[0] in {'-'}:
      _reverse_diff(exp[1], adjoint)
      _reverse_diff(exp[2], ["Neg", adjoint])
      return

    if exp[0] in {'*'}:
      left = exp[1]
      right = exp[2]
      _reverse_diff(exp[1], ["*", adjoint, left])
      _reverse_diff(exp[2], ["*", adjoint, right])
      return

    if exp[0] in {'/'}:
      upper = exp[1]
      lower = exp[2]
      _reverse_diff(exp[1], ["/", adjoint, upper])
      _reverse_diff(exp[2], ["/", ["*", ["Neg", adjoint], upper], ["pow", lower, ["Integer", "2"]]]) #"-({})*{}/{}**2".format(adjoint, high, low))
      return

    if exp[0] in {"exp"}:
      expo = exp[1]
      _reverse_diff(exp[1], ["*", ["exp", expo], adjoint]) #"exp({})*{}".format(base, adjoint))
      return

    if exp[0] in {"log"}:
      base = exp[1]
      _reverse_diff(exp[1], ["/", adjoint, base]) #"1/{}*{}".format(base, adjoint))
      return

    if exp[0] in {"pow", "powi"}:
      base = exp[1]
      expo = exp[2]
      _reverse_diff(exp[1], ['*', adjoint, ['*', expo, ['powi', base, ['-', expo, ['Integer', "1"]]]]])
                    #"{}*{}*{}**({}-1)".format(adjoint, expo, base, expo))
      _reverse_diff(exp[2], ['*', adjoint, ['*', ['log', base], ['powi', base, expo]]])
                    #"{}*math.log({})*{}**{}".format(adjoint, base, base, expo))
      return

    if exp[0] in {"Neg"}:
      _reverse_diff(exp[1], ["Neg", adjoint]) #"-({})".format(adjoint))
      return

    if exp[0] in {"Variable"}:
      _reverse_diff(assigns[exp[1]], adjoint)
      return

    if exp[0] in {"Return"}:
      _reverse_diff(exp[1], adjoint)
      return

    if exp[0] in {"Integer", "Float"}:
      return

    print("reverse_diff error unknown: '{}'".format(exp))
    sys.exit(-1)

  #exp = single_assignment(exp, inputs, assigns, consts)
  _reverse_diff(exp, ["Integer", "1"])
  result = ["Box"]+[d for d in gradient.values()]
  # for k in gradient:
  #   new_exp = single_assignment(["Return", gradient[k]], inputs, assigns, consts)
  #   gradient[k] = new_exp
  return ["Tuple", exp, result]








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_consts import lift_consts
  from pass_lift_assigns import lift_assigns
  from pass_pow import pow_replacement
  from output_rust import to_rust
  from pass_single_assignment import single_assignment

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  assigns = lift_assigns(exp, inputs)
  consts = lift_consts(exp, inputs, assigns)
  pow_replacement(exp, inputs, assigns, consts)

  exp = reverse_diff(exp, inputs, assigns, consts)
  consts = lift_consts(exp, inputs, assigns, consts)
  single_assignment(exp, inputs, assigns, consts)

  print("reverse_diff:")
  print(to_rust(exp, inputs, assigns, consts)[0])
  print()
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
