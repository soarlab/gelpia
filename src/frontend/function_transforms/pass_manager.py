#!/usr/bin/env python3

import sys

from lexed_to_parsed import BINOPS, UNOPS

BINOPS.update({'+', '-', '*', '/', 'powi'})
UNOPS.update({'Neg'})
INFIX = {'+', '-', '*', '/'}

def strip_arc(f):
    d = {"arccos"  : "acos",
         "arcsin"  : "asin",
         "arctan"  : "atan",
         "arccosh" : "acosh",
         "argcosh" : "acosh",
         "arcosh"  : "acosh",
         "arcsinh" : "asinh",
         "argsinh" : "asinh",
         "arsinh"  : "asinh",
         "arctanh" : "atanh",
         "argtanh" : "atanh",
         "artanh"  : "atanh"}
    if f in d.keys():
        return d[f]
    return f


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

  return data

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
