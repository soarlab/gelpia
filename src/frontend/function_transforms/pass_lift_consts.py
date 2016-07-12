#!/usr/bin/env python3

from pass_manager import *

import sys


def lift_consts(exp, inputs):
  consts = list()
  
  def make_constant(exp):
    try:
      i = consts.index(exp)
    except ValueError:
      i = len(consts)
      consts.append(exp[:])
    exp[0] = 'Const'
    exp[1] = '{}'.format(i)
    del exp[2:]
  
      
  def _lift_consts(exp):
    if type(exp[0]) is list:
      _lift_consts(exp[0])
      _lift_consts(exp[1])
      return False

    if exp[0] in UNIOPS.union({"ipow"}):
      return _lift_consts(exp[1])
      
    if exp[0] in BINOPS:
      first  = _lift_consts(exp[1])
      second = _lift_consts(exp[2])
      if first and second:
        return True
      elif first:
        make_constant(exp[1])
      elif second:
        make_constant(exp[2])
      return False      

    if exp[0] in {"InputInterval", "Variable", "Input"}:
      return False
    
    if exp[0] in {"ConstantInterval", "Float", "Integer", "Symbol"}:
      return True
    
    if exp[0] in {"Return"}:
      if _lift_consts(exp[1]):
        make_constant(exp[1])
      return False
        
    if exp[0] in {"Assign"}:
      if _lift_consts(exp[2]):
        make_constant(exp[2])
      return False
        
    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)

    
  _lift_consts(exp)
  return consts
            
            
            





def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
    
  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  consts = lift_consts(exp, inputs)

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
