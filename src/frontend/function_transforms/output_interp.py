#!/usr/bin/env python3

from pass_manager import *

import sys


def to_interp(exp, consts, inputs, assign):
  input_names = [name for name in inputs]
  
  def _to_interp(exp):
    if exp[0] in {"ipow"}:
      return _to_interp(exp[1]) + ["p{}".format(exp[2][1])]

    if exp[0] in {"pow"}:
      return _to_interp(exp[1]) + _to_interp(exp[2]) + ['op']
    
    if exp[0] in INFIX:
      return _to_interp(exp[1]) + _to_interp(exp[2]) + ['o'+exp[0]]

    if exp[0] in UNIOPS:
      return _to_interp(exp[1]) + ['f'+exp[0].lower()]

    if exp[0] in {"Const"}:
      return ['c'+exp[1]]
    
    if exp[0] in {"Input"}:
      return ['i'+str(input_names.index(exp[1]))]

    if exp[0] in {"Variable"}:
      return _to_interp(assign[exp[1]])

    if exp[0] in {"Return"}:
      return _to_interp(exp[1])
                                          
    print("to_interp error unknown: '{}'".format(exp))
    sys.exit(-1)


  return ','.join(_to_interp(exp))








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
  function = to_interp(exp, consts, inputs, assign)
    
  print("-Interp Version-")
  print("function:")
  print(function)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)
    
if __name__ == '__main__':
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
