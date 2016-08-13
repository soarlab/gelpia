#!/usr/bin/env python3

from pass_manager import *
import collections
import sys


def to_rust(exp, inputs, assigns, consts):
  let = "    let {} = {};\n"
  lp = ['(']
  rp = [')']
  lb = ['[']
  rb = [']']
  cm = [',']
  sp = [' ']
  diff_decl = ["extern crate gr;\n"
               "use gr::*;\n"
               "\n"
               "#[no_mangle]\n"
               "pub extern \"C\"\n"
               "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> (GI, Option<Vec<GI>>) {\n"]
  decl = ["extern crate gr;\n"
          "use gr::*;\n"
          "\n"
          "#[no_mangle]\n"
          "pub extern \"C\"\n"
          "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> (GI) {\n"]
  input_names = [name for name in inputs]

  def _to_rust(exp):
    nonlocal decl
    if exp[0] in {"Integer", "Float"}:
      return lb + [exp[1]] + rb

    if exp[0] in {"pow"}:
      e = exp[2][1]
      return ["pow"] + lp + _to_rust(exp[1]) + cm + [e] + rp

    if exp[0]in {"powi"}:
      return ["powi"] + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp

    if exp[0] in {"Neg"}:
      return ['-'] + lp + _to_rust(exp[1]) + rp

    if exp[0] in INFIX:
      return lp + _to_rust(exp[1]) + [exp[0]] + _to_rust(exp[2]) + rp

    if exp[0] in BINOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp

    if exp[0] in UNOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + rp

    if exp[0] in {"Symbol"}:
      return [exp[1]]

    if exp[0] in {"InputInterval"}:
      inside = _to_rust(exp[1]) + cm + _to_rust(exp[2])
      inside = [part for part in inside if part != ']' and part != '[']
      return lb + inside + rb

    if exp[0] in {"Const"}:
      return ["_c[{}]".format(list(consts.keys()).index(exp[1]))]

    if exp[0] in {"Input"}:
      return ["_x[{}]".format(input_names.index(exp[1]))]

    if exp[0] in {"Variable"}:
      return [exp[1]]

    if exp[0] in {"ConstantInterval"}:
      if len(exp) == 2:
        return _to_rust(exp[1])
      elif len(exp) == 3:
        inside = _to_rust(exp[1]) + cm + _to_rust(exp[2])
        inside = [part for part in inside if part != ']' and part != '[']
        return lb + inside + rb
      else:
        print("Error in constant outputting for rust")
        sys.exit(-1)

    if exp[0] in {"Tuple"}:
      decl = diff_decl
      return ["("] + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + [")"]

    if exp[0] in {"Box"}:
      val = ["Some(vec!"] + lb
      for part in exp[1:]:
        val += _to_rust(part) + cm + sp
      if val[-2:] == [cm, sp]:
        del val[-2:]
      val += rb + [")"]
      return val

    if exp[0] in {"Return"}:
      return _to_rust(exp[1])

    print("to_rust error unknown: '{}'".format(exp))
    sys.exit(-1)

  function = [let.format(n, ''.join(_to_rust(v))) for n,v in assigns.items()]
  function += ["    "] + _to_rust(exp) + ["\n}\n"]

  new_inputs = [(n, ''.join(_to_rust(v))) for n,v in inputs.items()]
  new_inputs = collections.OrderedDict(new_inputs)

  new_consts = collections.OrderedDict([(k,(''.join(_to_rust(v))).replace("powi","pow")) for k,v in consts.items()])

  return ''.join(decl+function), new_inputs, new_consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs import lift_inputs
  from pass_lift_consts import lift_consts
  from pass_lift_assigns import lift_assigns

  data = get_runmain_input()
  exp = parse_function(data)
  inputs = lift_inputs(exp)
  assigns = lift_assigns(exp, inputs)
  consts = lift_consts(exp, inputs, assigns)

  function, new_inputs, new_consts = to_rust(exp, inputs, assigns, consts)

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
