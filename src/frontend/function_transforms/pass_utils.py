#!/usr/bin/env python3

import re
import sys

from function_to_lexed import BINOPS, UNOPS

BINOPS.update({'+', '-', '*', '/', 'powi'})
UNOPS.update({'neg', "dabs", "datanh"})
INFIX = {'+', '-', '*', '/'}


bops = {'+'    : lambda l,r:str(int(l[1])+int(r[1])),
        '-'    : lambda l,r:str(int(l[1])-int(r[1])),
        '*'    : lambda l,r:str(int(l[1])*int(r[1])),
        'pow'  : lambda l,r:str(int(l[1])**int(r[1])),
        'powi' : lambda l,r:str(int(l[1])**int(r[1])),}
uops = {'neg': lambda a:str(-int(a[1]))}


def expand(exp, assigns=None, consts=None, cache=dict()):
  if exp in cache:
    return cache[exp]

  tag = exp[0]

  if tag in BINOPS:
    l = expand(exp[1], assigns, consts)
    r = expand(exp[2], assigns, consts)
    if tag in bops:
      if l[0] == "Integer" and r[0] == "Integer":
        return ("Integer", bops[tag](l, r))
      if tag == "powi" and r[0] == "Integer":
        return ("pow", l, r)
    return (exp[0], l, r)

  if tag in UNOPS:
    a = expand(exp[1], assigns, consts)
    if tag in uops:
      if a[0] == "Integer":
        return ("Integer", uops[tag](a))
    return (exp[0], a)

  if tag in {"Const"}:
    return consts[exp[1]]

  if tag in {"Variable"}:
    return expand(assigns[exp[1]], assigns, consts)

  if tag in {"Input", "Integer", "Float", "ConstantInterval", "PointInterval"}:
    return exp

  if tag in {"Box"}:
    return ("Box",) + tuple(expand(e, assigns, consts) for e in exp[1:])

  print("Internal error in expand: {}".format(exp))
  sys.exit(-1)


def print_exp(exp):
  print("expressions:")
  while type(exp[0]) is tuple:
    print(exp[0])
    exp = exp[1]
  print(exp)


def _print_dict(di, label):
  print("{}:".format(label))
  for key,val in di.items():
    print("{} = {}".format(key, val))


def print_inputs(inputs):
  _print_dict(inputs, "inputs")


def print_consts(consts):
  _print_dict(consts, "consts")


def print_assigns(assigns):
  _print_dict(assigns, "assigns")


def get_runmain_input():
  try:
    filename = sys.argv[1]
    with open(filename, "r") as f:
      data = f.read()
  except IndexError:
    sys.stdout.write("Reading from standard input (type EOF to end):\n")
    data = sys.stdin.read()

  # vars
  lines = [line.strip() for line in data.splitlines() if line.strip()!='']
  try:
    start = lines.index("var:")
  except:
    return data


  var_lines = list()
  names = set()
  for line in lines[start+1:]:
    if ':' in line:
      break
    match = re.search(r"(\[[^,]+, *[^\]]+\]) *([^;]+)", line)
    if match:
      val = match.group(1)
      name = match.group(2)
      if name in names:
        print("Duplicate variable definition {}".format(name))
        sys.exit(-1)
      names.add(name)
    else:
      print("Malformed query file, imporoper var: {}".format(line))
      sys.exit(-1)
    var_lines.append("{} = {};".format(name, val))
  var_lines = '\n'.join(var_lines)

  # cost
  try:
    start = lines.index("cost:")
  except:
    print("Malformed query file, no cost section: {}".format(filename))
    sys.exit(-1)
  function = list()
  for line in lines[start+1:]:
    if ':' in line:
      break
    function.append("({})".format(line.replace(';','')))
  function = '+'.join(function)

  # constraints
  try:
    start = lines.index("ctr:")
  except:
    start = False

  constraints = list()
  if start:
    for line in lines[start+1:]:
      if ':' in line:
        break
      constraints.append(line)
    print("Gelpia does not currently handle constraints")
    sys.exit(-1)

  constraints = '\n'.join(constraints)

  # combining and parsing
  return '\n'.join((var_lines, constraints, function))
