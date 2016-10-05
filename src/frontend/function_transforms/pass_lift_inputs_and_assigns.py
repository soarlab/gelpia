#!/usr/bin/env python3

import collections # OrderedDict
import sys         # exit

from pass_utils import UNOPS, BINOPS


def lift_inputs_and_assigns(exp):
  """ Extracts input variables and assignments from an expression """

  # Constants
  ATOMS     = {"ConstantInterval", "PointInterval", "Float", "Integer", "Input",
               "Variable"}
  ONE_ITEM  = UNOPS.union({"Return"})

  # Function local variables
  assigns      = collections.OrderedDict() # name -> expression
  used_assigns = set()                     # assignments seen in the main exp
  inputs       = collections.OrderedDict() # name -> input range
  used_inputs  = set()                     # inputs seen in the main exp
  implicit_input_count = 0                 # number of implicit inputs

  # increase stack size for saftey
  old_limit = sys.getrecursionlimit()
  sys.setrecursionlimit(4000)

  def _lift_inputs_and_assigns(exp):
    nonlocal implicit_input_count
    tag = exp[0]


    # A leading tuple must be an assign
    if type(tag) is tuple:
      assignment = exp[0]
      assert(assignment[0] == "Assign")
      name = assignment[1]
      assert(name[0] == "Name")
      val  = assignment[2]
      # Explicit inputs
      if val[0] == "InputInterval":
        assert(name[1] not in inputs)
        inputs[name[1]] = val

      # Assignment to an expression
      else:
        assert(name[1] not in assigns)
        assigns[name[1]] = _lift_inputs_and_assigns(val)

      # Work on the rest of the expression
      return  _lift_inputs_and_assigns(exp[1])


    # Recur on arguments
    if tag in BINOPS:
      l = _lift_inputs_and_assigns(exp[1])
      r = _lift_inputs_and_assigns(exp[2])
      return (exp[0], l, r)


    # Recur on argument
    if tag in ONE_ITEM:
      arg = _lift_inputs_and_assigns(exp[1])
      return (exp[0], arg)


    # Base cases
    if tag in ATOMS:
      return exp


    # If we get here a bare range was given in the middle of an expression
    # This is turned into an implicit input
    if tag == "InputInterval":
      return ("ConstantInterval", exp[1], exp[2])
      # Temporarily disabled
      interval     = exp[:]
      name         = "$_implicit_Input_{}".format(implicit_input_count)
      new_exp      = ("Input", name)
      assert(name not in inputs)
      inputs[name] = interval
      implicit_input_count += 1
      used_inputs.add(name)
      return new_exp


    # Change generic 'Name' to specific tags
    if tag == "Name":

      # Input
      if exp[1] in inputs:
        used_inputs.add(exp[1])
        assert(exp[1] not in assigns)
        return ("Input", exp[1])

      # Assignment
      elif exp[1] in assigns:
        used_assigns.add(exp[1])
        return ("Variable", exp[1])

      # Not a valid 'Name'
      print("Use of undeclared name: {}".format(exp[1]))
      sys.exit(-1)


    # exp is not in the laguage
    print("lift_inputs_and_assigns error unknown: '{}'".format(exp))
    sys.exit(-1)


  # Call internally scoped function
  new_exp = _lift_inputs_and_assigns(exp)

  # Remove dead inputs
  dead_inputs = set(inputs).difference(used_inputs)
  for k in dead_inputs:
    del inputs[k]

  # Remove dead assigns
  dead_assigns = set(assigns).difference(used_assigns)
  for k in dead_assigns:
    del assigns[k]

  # reset stack size
  sys.setrecurionlimit(old_limit)
  return new_exp, inputs, assigns








def runmain():
  from pass_utils import get_runmain_input
  from lexed_to_parsed import parse_function
  from pass_utils import print_exp, print_inputs, print_assigns

  data = get_runmain_input()
  exp  = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)

  print_inputs(inputs)
  print()
  print_assigns(assigns)
  print()
  print_exp(exp)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
