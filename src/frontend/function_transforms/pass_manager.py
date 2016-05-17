#!/usr/bin/env python3

import sys

from lexed_to_parsed import BINOPS, UNIOPS

BINOPS.update({'+', '-', '*', '/', 'ipow'})
UNIOPS.update({'Neg'})

def print_exp(exp):
  print("expressions:")
  while type(exp[0]) is list:
    print(exp[0])
    exp = exp[1]
  print(exp)


def _print_dict(di, label):
  print("{}:".format(label))
  for name,val in di.items():
    print("{} = {}".format(name, val))

    
def print_inputs(inputs):
  _print_dict(inputs, "inputs")

  
def print_consts(consts):
  _print_dict(dict(enumerate(consts)), "consts")

    
def print_assign(assign):
  _print_dict(assign, "assign")


def get_runmain_input():
  try:
    filename = sys.argv[1]
    with open(filename, "r") as f:
      data = f.read()
  except IndexError:
    sys.stdout.write("Reading from standard input (type EOF to end):\n")
    data = sys.stdin.read()

  return data

