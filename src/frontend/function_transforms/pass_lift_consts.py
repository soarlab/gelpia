#!/usr/bin/env python3

import collections # OrderedDict
import sys         # exit

from pass_utils import UNOPS, BINOPS, expand


def lift_consts(exp, inputs, assigns, consts=None, hashed=dict()):
  """ Extracts constant values from an expression """
  # Note about hashed: This argument should never be used, it is there to
  #   work as a static variable, and it must be declared in the outermost
  #   function scope to achieve this. It is not a global to avoid name clashes.

  # Constants
  CONST = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}
  NON_CONST_UNOPS = {"sinh", "cosh", "tanh", "dabs", "datanh"}

  # Const dict can be updated or created
  if consts == None:
    consts = collections.OrderedDict()

  assign_status = dict() # const status of assignments


  def make_constant(exp):
    if exp[0] == "Const":
      assert(exp[1] in consts)
      return exp
    new_exp = expand(exp, assigns, consts) # BAD

    # It's Better To Beg For Forgiveness Than Ask For Permission ...
    try:
      key = hashed[new_exp]
    except KeyError:
      key = "$_const_{}".format(len(hashed))
      assert(new_exp not in hashed)
      hashed[new_exp] = key
      assert(key not in consts)
      consts[key] = new_exp

    return ('Const', key)



  def _lift_consts(exp):
    # Return is a tuple: (is_expression_const_p, expression)
    tag = exp[0]


    # Recur on arguments
    if tag in BINOPS:
      l, left  = _lift_consts(exp[1])
      r, right = _lift_consts(exp[2])

      # Elivate 'powi' to 'pow' if the exponent is an integer
      if tag == "powi" and r:
        e = expand(exp[2], assigns, consts) # BAD
        if e[0] == "Integer":
          return l, ("pow", left, e)

      # If both are constant don't consolidate yet
      if l and r:
        return True, (exp[0], left, right)

      # Otherwise consolidate any arguments that are constant
      elif l:
        left = make_constant(exp[1])
      elif r:
        right = make_constant(exp[2])

      return False, (exp[0], left, right)


    # Positive base cases
    if tag in CONST:
      return True, exp


    # Negative base case
    if tag == "Input":
      return False, exp


    # Get assign status
    if tag == "Variable":
      if assign_status[exp[1]]:
        return True, assigns[exp[1]]
      return False, exp


    # Recur on arguments
    if tag in UNOPS:
      a, arg = _lift_consts(exp[1])

      # MB: Crlibm is claimed to not be ULP accurate by GAOL. Hence, we must
      # MB: defer to implementations based on the exponential function.
      if tag in NON_CONST_UNOPS:
        if a:
          arg = make_constant(exp[1])
        return False, (exp[0], arg)

      return a, (exp[0], arg)


    # If return is constant we have an early out
    if tag == "Return":
      n, new_exp = _lift_consts(exp[1])
      if n:
        new_exp = make_constant(exp[1])
      return n, ("Return", new_exp)


    # Recur on arguments
    if tag == "Tuple":
      l, left  = _lift_consts(exp[1])
      r, right = _lift_consts(exp[2])
      if l:
        left = make_constant(exp[1])
      if r:
        right = make_constant(exp[2])
      return False, ("Tuple", left, right)


    # Recur on arguments
    if tag == "Box":
      rest = list()

      # Process box contents
      for i in range(1, len(exp)):
        p, part = _lift_consts(exp[i])
        if p:
          part = make_constant(exp[i])
        rest.append(part)

      return False, ("Box",)+tuple(rest)


    # exp is not in the laguage
    print("lift_consts error unknown: '{}'".format(exp))
    sys.exit(-1)


  # Go over the assigns
  for name, val in assigns.items():
    status, new_value = _lift_consts(val)
    assigns[name] = new_value
    assign_status[name] = status

  # Call on base expression, a 'Return'
  n, new_exp = _lift_consts(exp)

  # Remove assigns which are to consts
  for name, status in assign_status.items():
    if status:
      # TODO
      assigns[name] = make_constant(assigns[name])

  return n, new_exp, consts








def runmain():
  from pass_utils import get_runmain_input
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_utils import print_exp, print_inputs, print_assigns, print_consts

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  e, exp, consts = lift_consts(exp, inputs, assigns)

  print_inputs(inputs)
  print()
  print_consts(consts)
  print()
  print_assigns(assigns)
  print()
  print_exp(exp)
  print()
  print("Const: {}".format(e))


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
