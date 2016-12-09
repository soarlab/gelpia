#!/usr/bin/env python3

from pass_utils import *
from expression_walker import walk
import sys


def to_interp(exp, inputs, assigns, consts):
  input_names = [name for name in inputs]
  const_names = [name for name in consts]


  def _const(work_stack, count, exp):
    assert(exp[0] == "Const")
    assert(len(exp) == 2)
    work_stack.append((True, count,  ['c'+str(const_names.index(exp[1]))]))

  def _input(work_stack, count, exp):
    assert(exp[0] == "Input")
    assert(len(exp) == 2)
    work_stack.append((True, count,  ['i'+str(input_names.index(exp[1]))]))

  def _variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 2)
    work_stack.append((False, count, assigns[exp[1]]))

  my_expand_dict = {"Const":    _const,
                    "Input":    _input,
                    "Variable": _variable}




  def _pow(work_stack, count, args):
    assert(args[0] == "pow")
    assert(len(args) == 3)
    assert(args[2][0] == "Integer")
    assert(type(args[1]) is list)
    work_stack.append((True, count, args[1] + ["p"+args[2][1]]))

  def _sub2(work_stack, count, args):
    assert(args[0] == "sub2")
    assert(len(args) == 3)
    assert(type(args[1]) is list)
    assert(type(args[2]) is list)
    work_stack.append((True, count, args[1] + args[2] + ["osub2"]))

  def _powi(work_stack, count, args):
    assert(args[0] == "powi")
    assert(len(args) == 3)
    assert(type(args[1]) is list)
    assert(type(args[2]) is list)
    work_stack.append((True, count, args[1] + args[2] + ["op"]))

  def _infix(work_stack, count, args):
    assert(args[0] in INFIX)
    assert(len(args) == 3)
    assert(type(args[1]) is list)
    assert(type(args[2]) is list)
    work_stack.append((True, count, args[1] + args[2] + ["o"+args[0]]))

  def _unops(work_stack, count, args):
    assert(args[0] in UNOPS)
    assert(len(args) == 2)
    assert(type(args[1]) is list)
    work_stack.append((True, count, args[1] + ["f"+args[0].lower()]))

  def _return(work_stack, count, args):
    assert(args[0] == "Return")
    assert(len(args) == 2)
    return args[1]

  my_contract_dict = dict()
  my_contract_dict.update(zip(INFIX, [_infix for _ in INFIX]))
  my_contract_dict.update(zip(UNOPS, [_unops for _ in UNOPS]))
  my_contract_dict["pow"]  = _pow
  my_contract_dict["powi"] = _powi
  my_contract_dict["sub2"] = _sub2
  my_contract_dict["Return"] = _return

  exp = walk(my_expand_dict, my_contract_dict, exp, assigns)

  try:
    return ','.join(exp)
  except:
    print(exp)
    sys.exit(-1)







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
  consts = lift_consts(exp, inputs, assigns, consts)

  function = to_interp(exp, inputs, assigns, consts)

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
