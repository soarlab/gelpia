#!/usr/bin/env python3

import collections # OrderedDict
import sys         # exit

from pass_utils import *


def reverse_diff(exp, inputs, assigns, consts=None):
  """
  Performs reverse accumulated automatic differentiation of the given exp
    for all variables
  """

  # Constants
  UNUSED = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}
  POWS   = {"pow", "powi"}

  # Function local variables
  gradient = collections.OrderedDict([(k,("Integer","0")) for k in inputs])


  def _reverse_diff(exp, adjoint):
    tag = exp[0]

    if tag in UNUSED:
      return

    if tag == "Input":
      old = gradient[exp[1]]
      if old == ("Integer", "0"):
        gradient[exp[1]] = adjoint
      else:
        gradient[exp[1]] = ("+", old, adjoint)
      return


    # All the cases for supported operators

    if tag == "+":
       _reverse_diff(exp[1], adjoint)
       _reverse_diff(exp[2], adjoint)
       return

    if tag == "-":
      _reverse_diff(exp[1], adjoint)
      _reverse_diff(exp[2], ("neg", adjoint))
      return

    if tag == "*":
      left = exp[1]
      right = exp[2]
      _reverse_diff(exp[1], ("*", adjoint, right))
      _reverse_diff(exp[2], ("*", adjoint, left))
      return

    if tag == "/":
      upper = exp[1]
      lower = exp[2]
      _reverse_diff(exp[1], ("/", adjoint, lower))
      _reverse_diff(exp[2], ("/", ("*", ("neg", adjoint), upper),
                             ("pow", lower, ("Integer", "2"))))
      return

    if tag in POWS:
      base = exp[1]
      expo = exp[2]
      _reverse_diff(exp[1], ("*", adjoint, ("*", expo,
                                            ("powi", base,
                                             ("-", expo, ("Integer", "1"))))))
      _reverse_diff(exp[2], ("*", adjoint, ("*", ("log", base),
                                            ("powi", base, expo))))
      return

    if tag == "neg":
      _reverse_diff(exp[1], ("neg", adjoint))
      return

    if tag == "exp":
      expo = exp[1]
      _reverse_diff(exp[1], ("*", ("exp", expo), adjoint))
      return

    if tag == "log":
      base = exp[1]
      _reverse_diff(exp[1], ("/", adjoint, base))
      return

    if tag == "sqrt":
      x = exp[1]
      _reverse_diff(exp[1], ("/", adjoint, ("*", ("Integer", "2"),
                                            ("sqrt", x))))
      return

    if tag == "cos":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("neg", ("sin", x)), adjoint))
      return

    if tag == "acos":
      x = exp[1]
      _reverse_diff(exp[1], ("neg", ("/", adjoint,
                                     ("sqrt", ("-",
                                               ("Integer", "1"),
                                               ("pow", x,
                                                ("Integer", "2")))))))
      return

    if tag == "sin":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("cos", x), adjoint))
      return

    if tag == "asin":
      x = exp[1]
      _reverse_diff(exp[1], ("/", adjoint, ("sqrt", ("-", ("Integer", "1"),
                                                     ("pow", x,
                                                      ("Integer", "2"))))))
      return

    if tag == "tan":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("+", ("Integer", "1"),
                                   ("pow", ("tan", x),
                                    ("Integer", "2"))), adjoint))
      return

    if tag == "atan":
      x = exp[1]
      _reverse_diff(exp[1], ("/", adjoint, ("+", ("Integer", "1"),
                                            ("pow", x, ("Integer", "2")))))
      return

    if tag == "cosh":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("sinh", x), adjoint))
      return


    if tag == "sinh":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("cosh", x), adjoint))
      return

    if tag == "asinh":
      x = exp[1]
      _reverse_diff(exp[1], ("/", adjoint,
                             ("sqrt", ("+", ("pow", x, ("Integer", "2")),
                                       ("Integer", "1")))))
      return

    if tag == "tanh":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("-", ("Integer", "1"),
                                   ("pow", ("tanh", x),
                                    ("Integer", "2"))), adjoint))
      return

    if tag == "abs":
      x = exp[1]
      _reverse_diff(exp[1], ("*", ("dabs", x), adjoint))
      return

    # Recur
    if tag == "Variable":
      _reverse_diff(assigns[exp[1]], adjoint)
      return

    # Recur
    if tag == "Return":
      _reverse_diff(exp[1], adjoint)
      return

    print("reverse_diff error unknown: tag = '{}'\nfull={}".format(tag, exp))
    sys.exit(-1)


  _reverse_diff(exp, ("Integer", "1"))
  result = ("Box",) + tuple(d for d in gradient.values())
  retval = ("Return", ("Tuple", exp[1], result))

  return retval








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_dead_removal import dead_removal
  from pass_simplify import simplify
  from output_rust import to_rust
  from pass_single_assignment import single_assignment

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  e, exp, consts = lift_consts(exp, inputs, assigns)
  dead_removal(exp, inputs, assigns, consts)

  exp = reverse_diff(exp, inputs, assigns, consts)
  exp = simplify(exp, inputs, assigns, consts)

  if len(sys.argv) == 3 and sys.argv[2] == "test":
    assert(exp[0] == "Return")
    tup = exp[1]
    assert(tup[0] == "Tuple")
    box = tup[2]
    if box[0] == "Const":
      const = box
      assert(const[0] == "Const")
      box = expand(const, assigns, consts)

    assert(box[0] == "Box")
    if len(box) == 1:
      print("No input variables")
      assert(len(inputs) == 0)
      return

    for name, diff in zip(inputs.keys(), box[1:]):
        print("d{} = {}".format(name, expand(diff, assigns, consts)))

  else:
    single_assignment(exp, inputs, assigns, consts)
    print("reverse_diff:")
    print_exp(exp)
    print()
    print_inputs(inputs)
    print()
    print_consts(consts)
    print()
    print_assigns(assigns)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
