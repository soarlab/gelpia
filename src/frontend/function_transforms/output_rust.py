#!/usr/bin/env python3

from pass_manager import *

import collections
import sys


def to_rust(exp, consts, inputs, assign):
  let = "    let {} = {};\n"
  lp = ['(']
  rp = [')']
  lb = ['[']
  rb = [']']
  cm = [',']
  function = ["extern crate gr;\n"
              "use gr::*;\n"
              "\n"
              "#[no_mangle]\n"
              "pub extern \"C\"\n"
              "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {\n"]
  input_names = [name for name in inputs]
  
  def _to_rust(exp):
    if exp[0] in {"ipow"}:
      return ["pow"] + lp + _to_rust(exp[1]) + cm + [exp[2][1]] + rp

    if exp[0]in {"pow"}:
      return ["powi"] + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp
    
    if exp[0] in {"Neg"}:
      return ['-'] + lp + _to_rust(exp[1]) + rp    

    if exp[0] in INFIX:
      return lp + _to_rust(exp[1]) + [exp[0]] + _to_rust(exp[2]) + rp

    if exp[0] in BINOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp
      
    if exp[0] in UNIOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + rp

    if exp[0] in {"Integer", "Float"}:
      return lb + [exp[1]] + rb

    if exp[0] in {"InputInterval"}:
      inside = _to_rust(exp[1]) + cm + _to_rust(exp[2])
      inside = [part for part in inside if part != ']' and part != '[']
      return lb + inside + rb

    if exp[0] in {"Const"}:
      return ["_c[{}]".format(exp[1])]
    
    if exp[0] in {"Input"}:
      return ["_x[{}]".format(input_names.index(exp[1]))]

    if exp[0] in {"Variable"}:
      return _to_rust(assign[exp[1]])

    if exp[0] in {"Return", "ConstantInterval"}:
      return _to_rust(exp[1])
                                          
    print("to_rust error unknown: '{}'".format(exp))
    sys.exit(-1)


  function += [let.format(n, ''.join(_to_rust(v))) for n,v in assign.items()]
  function += ["    "] + _to_rust(exp) + ["\n}\n"]

  new_inputs = [(n, ''.join(_to_rust(v))) for n,v in inputs.items()]
  new_inputs = collections.OrderedDict(new_inputs)

  new_consts = [''.join(_to_rust(c)) for c in consts]
    
  return ''.join(function), new_inputs, new_consts

 






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
  function, new_inputs, new_consts = to_rust(exp, consts, inputs, assign)

  print("-Rust Version-")
  print("function:")
  print(function)
  print()
  print_inputs(new_inputs)
  print()
  print_consts(new_consts)
  
if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
