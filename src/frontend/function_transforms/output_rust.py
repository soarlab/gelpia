#!/usr/bin/env python3

from pass_utils import *

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
               "#[allow(unused_parens)]\n"
               "#[no_mangle]\n"
               "pub extern \"C\"\n"
               "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> (GI, Option<Vec<GI>>) {\n"]
  decl = ["extern crate gr;\n"
          "use gr::*;\n"
          "\n"
          "#[no_mangle]\n"
          "pub extern \"C\"\n"
          "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> (GI) {\n"]
  powi = ["powi"]
  doing_consts = False
  input_names = [name for name in inputs]
  const_names = [name for name in consts]

  def _to_rust(exp):
    nonlocal decl
    typ = exp[0]
    if doing_consts and typ in {"Integer", "Float"}:
      return lb + [exp[1]] + rb

    if typ == "pow":
      e = expand(exp[2], assigns, consts)
      assert(e[0] == "Integer")
      return ["pow"] + lp + _to_rust(exp[1]) + cm + [e[1]] + rp

    if typ == "powi":
      e = expand(exp[2], assigns, consts)
      assert(e[0] != "Integer")
      return powi + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp

    if typ in INFIX:
      l = _to_rust(exp[1])
      r = _to_rust(exp[2])
      return lp + l + [exp[0]] + r + rp

    if typ in BINOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp

    if typ == "neg":
      return ["-"] + lp + _to_rust(exp[1]) + rp

    if typ in UNOPS:
      return [exp[0]] + lp + _to_rust(exp[1]) + rp

    if typ in {"InputInterval", "ConstantInterval"}:
      inside = [expand(exp[1], assigns, consts)[1]] + cm + [expand(exp[2], assigns, consts)[1]]
      return lb + inside + rb

    if typ in {"Const"}:
      return ["_c[{}]".format(const_names.index(exp[1]))]

    if typ in {"Input"}:
      return ["_x[{}]".format(input_names.index(exp[1]))]

    if typ in {"Variable"}:
      return [exp[1]]

    if typ in {"Tuple"}:
      decl = diff_decl
      return lp + _to_rust(exp[1]) + cm + _to_rust(exp[2]) + rp

    if typ in {"Box"}:
      if len(exp) == 1 and len(inputs) != 0:
        return ["None"]
        
      val = ["Some(vec!"] + lb
      for part in exp[1:]:
        val += _to_rust(part) + cm + sp
      if val[-2:] == [',', ' ']:
        del val[-2:]
      val += rb + rp
      return val

    if typ in {"Return", "PointInterval"}:
      return _to_rust(exp[1])


    print("to_rust error unknown: '{}'".format(exp))
    sys.exit(-1)


  function = [let.format(n, ''.join(_to_rust(v))) for n,v in assigns.items()]
  function += ["    "] + _to_rust(exp) + ["\n}\n"]

  new_inputs = [(n, ''.join(_to_rust(v))) for n,v in inputs.items()]
  new_inputs = collections.OrderedDict(new_inputs)

  powi = ["pow"]
  doing_consts = True
  new_consts = [(n, ''.join(_to_rust(v))) for n,v in consts.items()]
  new_consts = collections.OrderedDict(new_consts)

  return ''.join(decl+function), new_inputs, new_consts








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_simplify import simplify

  data = get_runmain_input()
  exp = parse_function(data)
  inputs, assigns = lift_inputs_and_assigns(exp)
  consts = lift_consts(exp, inputs, assigns)
  simplify(exp, inputs, assigns, consts)

  function, new_inputs, new_consts = to_rust(exp, inputs, assigns, consts)

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
