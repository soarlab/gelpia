#!/usr/bin/env python3

import re
import sys

from lexed_to_parsed import BINOPS, UNOPS

BINOPS.update({'+', '-', '*', '/', 'powi'})
UNOPS.update({'Neg', "dabs", "datanh"})
INFIX = {'+', '-', '*', '/'}


def print_exp(exp):
  print("expressions:")
  while type(exp[0]) is list:
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
    print("Malformed query file, no cost section: {}".format(args.query_file))
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


def exp_hash(exp, hashed=dict()):
    h = hash(str(exp))
    if h not in hashed:
        hashed[h] = len(hashed)
    return hashed[h]

def const_hash(exp):
    h = exp_hash(exp)
    return "_const_{}".format(h)

def cache_hash(exp):
    h = exp_hash(exp)
    return "_expr_{}".format(h)
