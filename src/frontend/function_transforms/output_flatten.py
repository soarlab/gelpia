#!/usr/bin/env python3

from pass_manager import *

import sys


def flatten(root, exp, inputs, consts, assign):
  lp = ['(']
  rp = [')']
  cm = [',']
  lb = ['[']
  rb = [']']
  
  def _flatten(exp):
    if type(exp[0]) is list:
      return _flatten(exp[1])

    if exp[0] in INFIX:
      return lp + _flatten(exp[1]) + [exp[0]] + _flatten(exp[2]) + rp

    if exp[0] in {"ipow"}:
      return ["pow"] + lp + _flatten(exp[1]) + cm + _flatten(exp[2]) + rp
  
    if exp[0] in BINOPS:
      return [exp[0]] + lp + _flatten(exp[1]) + cm + _flatten(exp[2]) + rp

    if exp[0] in UNIOPS:
      return [exp[0]] + lp + _flatten(exp[1]) + rp

    if exp[0] in {"Integer", "Float"}:
      return lb + [exp[1]] + rb

    if exp[0] in {"InputInterval"}:
      inside = _flatten(exp[1]) + cm + _flatten(exp[2])
      inside = [part for part in inside if part != ']' and part != '[']
      return lb + inside + rb

    if exp[0] in {"Const"}:
      return _flatten(consts[int(exp[1])])
    
    if exp[0] in {"Input"}:
      return _flatten(inputs[exp[1]])

    if exp[0] in {"Variable"}:
      return _flatten(assign[exp[1]])

    if exp[0] in {"Return", "ConstantInterval"}:
      return _flatten(exp[1])

    print("flatten error unknown: '{}'".format(exp))
    sys.exit(-1)

    
  return ''.join(_flatten(exp))



                                
                                



def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_consts import lift_consts
  from pass_lift_assign import lift_assign
  
  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  consts = lift_consts(exp, inputs)
  assign = lift_assign(exp, inputs, consts)
  flattened = flatten(exp, exp, inputs, consts, assign)
  
  print("flattened:")
  print(flattened)
  print()
  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)
  
if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
