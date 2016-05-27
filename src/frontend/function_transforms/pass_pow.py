#!/usr/bin/env python3

from pass_manager import *

import sys


def pow_replacement(exp, inputs, consts, assign):
  def expand(exp):
    mul_list = []
    def ipow(exp):
      if exp[0] == "ipow":
        expo = int(exp[2][1])
        if expo > 0:
          print("HERE")
          return [exp[1] for _ in range(expo)]
      return [exp]
        
    def _expand(exp):
      if exp[0] != "*":
        _pow_replacement(exp)
        mul_list.extend(ipow(exp))
      else:
        _pow_replacement(exp[2])
        mul_list.extend(ipow(exp[2]))
        _expand(exp[1])
    _expand(exp)
    mul_list.sort()
    return mul_list

  def compress(mul_list):
    exp = mul_list[0]
    expo = mul_list.count(exp)
    assert(expo != 0)
    while exp in mul_list:
      mul_list.remove(exp)
    if expo > 1:
      return ["ipow", exp, ["Integer", str(expo)]]
    return exp

  
  def _pow_replacement(exp, from_mul=False):
    if exp[0] in {'*'}:
      mul_list = expand(exp)
      left = compress(mul_list)

      if len(mul_list) == 0:
        for i in range(len(left)):
          exp[i] = left[i]
        return

      right = compress(mul_list)
      new_exp = ["*", left, right]
      while len(mul_list) > 0:
        temp = new_exp[:]
        new_exp = ["*", temp, compress(mul_list)]
      exp[1] = new_exp[1]
      exp[2] = new_exp[2]
      return

    if exp[0] in {"ipow"} and int(exp[2][1]) == 1:
      for i,e in enumerate(exp[1][:]):
        exp[i] = e
      return
    
    if exp[0] in BINOPS:
      _pow_replacement(exp[1])
      _pow_replacement(exp[2])
      return 
    
    if exp[0] in UNIOPS.union({"Return"}):
      _pow_replacement(exp[1])
      return

    if exp[0] in {"Variable"}:
      _pow_replacement(assign[exp[1]])
      return
      
    if exp[0] in {"ConstantInterval", "InputInterval", "Float", "Integer",
                  "Const", "Input"}:
      return

    print("pow_replacement error unknown: '{}'".format(exp))
    sys.exit(-1)

  _pow_replacement(exp)









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
  pow_replacement(exp, inputs, consts, assign)

  print_exp(exp)
  print()
  print_inputs(inputs)
  print()
  print_consts(consts)
  print()
  print_assign(assign)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
