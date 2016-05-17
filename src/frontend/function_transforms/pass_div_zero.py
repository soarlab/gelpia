#!/usr/bin/env python3

from pass_manager import *
from output_flatten import flatten

try:
  from gelpia import bin_dir
except:
  print("gelpia not found, gaol_repl must be in your PATH")
  bin_dir = ""
    
import re
import sys
import subprocess
import os.path as path


def div_by_zero(exp, inputs, consts, assign):
  query_proc = subprocess.Popen(path.join(bin_dir, 'gaol_repl'),
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                universal_newlines=True,
                                bufsize=0)
  root = exp
    
  def gaol_eval(exp):
    flat_exp = flatten(root, exp, inputs, consts, assign)
    query_proc.stdin.write('{}\n'.format(flat_exp))
    result = query_proc.stdout.readline()
    try:
      match = re.match("[<\[]([^,]+),([^>\]]+)[>\]]", result)
      l = float(match.group(1))
      r = float(match.group(2))
    except:
      print("query was: {}".format(flat_exp))
      print("unable to match: {}".format(result))
      sys.exit()
    return l,r
    
  def contains_zero(exp):
    l,r = gaol_eval(exp)
    return l<=0 and 0<=r

  def less_than_zero(exp):
    l,r = gaol_eval(exp)
    return l<0
    
  def _div_by_zero(exp):    
    if exp[0] in {'Float', 'Integer', 'ConstantInterval', 'InputInterval', 'Input'}:
      return False

    if exp[0] in {'/'}:
      return contains_zero(exp[2]) or _div_by_zero(exp[1]) or _div_by_zero(exp[2])

    if exp[0] in {"pow"}:
      temp = False
      if less_than_zero(exp[2]):
        temp = contains_zero(exp[1])
      return temp or _div_by_zero(exp[1]) or _div_by_zero(exp[2])
    
    if exp[0] in BINOPS:
      return _div_by_zero(exp[1]) or _div_by_zero(exp[2])

    if exp[0] in UNIOPS:
      return _div_by_zero(exp[1])

    if exp[0] in {"Variable"}:
      return _div_by_zero(assign[exp[1]])

    if exp[0] in {"Const"}:
      return _div_by_zero(consts[int(exp[1])])
    
    if exp[0] in {'Return'}:
      return _div_by_zero(exp[1])
    
    print("Error rewriting '{}'".format(exp))
    sys.exit(-1)
    
  result = _div_by_zero(exp)
  query_proc.communicate()
  return result


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
  has_div_zero = div_by_zero(exp, inputs, consts, assign)

  print("divides by zero:")
  print(has_div_zero)
  print()
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
