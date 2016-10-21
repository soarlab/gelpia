#!/usr/bin/env python3

import collections # OrderedDict
import sys         # exit

from pass_utils import UNOPS, BINOPS, expand
from expression_walker import walk


def lift_consts(exp, inputs, assigns, consts=None, hashed=dict()):
  """ Extracts constant values from an expression """
  # Note about hashed: This argument should never be used, it is there to
  #   work as a static variable, and it must be declared in the outermost
  #   function scope to achieve this. It is not a global to avoid name clashes.

  # Constants
  CONST = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}
  NON_CONST_UNOPS = {"sinh", "cosh", "tanh", "dabs", "datanh", "floor_power2",
                     "sym_interval"}

  # Const dict can be updated or created
  if consts == None:
    consts = collections.OrderedDict()

  assign_status = dict() # const status of assignments


  def make_constant(exp):
    if exp[0] == "Const":
      assert(exp[1] in consts)
      return exp

    # It's Better To Beg For Forgiveness Than Ask For Permission ...
    try:
      key = hashed[exp]
    except KeyError:
      key = "$_const_{}".format(len(hashed))
      assert(exp not in hashed)
      hashed[exp] = key
      assert(key not in consts)
      consts[key] = exp

    return ('Const', key)


  def _expand_positive_atom(work_stack, count, exp):
    work_stack.append((True, count, (*exp, True)))

  def _expand_negative_atom(work_stack, count, exp):
    assert(len(exp) == 2)
    work_stack.append((True, count, (exp[0], exp[1], False)))

  def _expand_variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 2)
    status = assign_status.get(exp[1], None)
    if status == None:
      work_stack.append((True,  count, exp[0]))
      work_stack.append((True,  2,     exp[1]))
      work_stack.append((False, 2,     assigns[exp[1]]))
    else:
      if status:
        work_stack.append((True,  count, (*assigns[exp[1]], status)))
      else:
        work_stack.append((True,  count, (exp[0], exp[1], False)))
  my_expand_dict = dict()
  my_expand_dict.update(zip(CONST, [_expand_positive_atom for _ in CONST]))
  my_expand_dict["Input"]    = _expand_negative_atom
  my_expand_dict["Variable"] = _expand_variable




  def _pow(work_stack, count, args):
    assert(args[0] in {"pow", "powi"})
    assert(len(args) == 3)
    l, left  = args[1][-1], args[1][:-1]
    r, right = args[2][-1], args[2][:-1]
    op = args[0]

    # Elivate 'powi' to 'pow' if the exponent is an integer
    if op == "powi" and r and right[0] == "Integer":
        op = "pow"

    # Don't lift pow exponents
    if op == "pow":
      r = False

    # If both are constant don't consolidate yet
    status = False
    if l and r:
      status = True
    # Otherwise consolidate any arguments that are constant
    elif l:
      left = make_constant(left)
    elif r:
      right = make_constant(right)

    work_stack.append((True, count, (op, left, right, status)))


  def _two_item(work_stack, count, args):
    assert(len(args) == 3)
    l, left  = args[1][-1], args[1][:-1]
    r, right = args[2][-1], args[2][:-1]
    op = args[0]

    # If both are constant don't consolidate yet
    status = False
    if l and r:
      status = True
    # Otherwise consolidate any arguments that are constant
    elif l:
      left = make_constant(left)
    elif r:
      right = make_constant(right)

    work_stack.append((True, count, (op, left, right, status)))


  def _tuple(work_stack, count, args):
    assert(args[0] == "Tuple")
    assert(len(args) == 3)
    l, left  = args[1][-1], args[1][:-1]
    if len(args[2]) == 1:
      r, right = False, args[2]
    else:
      r, right = args[2][-1], args[2][:-1]

    op = args[0]

    if l:
      left = make_constant(left)
    if r:
      right = make_constant(right)

    work_stack.append((True, count, (op, left, right, False)))


  def _one_item(work_stack, count, args):
    assert(len(args) == 2)
    a, arg = args[1][-1], args[1][:-1]
    op = args[0]

    work_stack.append((True, count, (op, arg, a)))


  def _bad_one_item(work_stack, count, args):
    assert(len(args) == 2)
    a, arg = args[1][-1], args[1][:-1]
    op = args[0]
    if a:
      arg = make_constant(arg)
    work_stack.append((True, count, (op, arg, False)))


  def _box(work_stack, count, args):
    assert(args[0] == "Box")
    box = ["Box"]
    for sub in args[1:]:
      p, part = sub[-1], sub[:-1]
      if p:
        part = make_constant(part)
      box.append(part)
    box.append(False)
    work_stack.append((True, count, tuple(box)))


  def _variable(work_stack, count, args):
    assert(args[0] == "Variable")
    assert(len(args) == 3)
    if args[2] == ("Box",):
      v, val = False, args[2]
    else:
      v, val = args[2][-1], args[2][:-1]
    assigns[args[1]] = val
    if v:
      work_stack.append((True, count, (*val, True)))
    else:
      work_stack.append((True, count, ("Variable", args[1], False)))

  def _return(work_stack, count, args):
    assert(args[0] == "Return")
    assert(len(args) == 2)
    r, retval = args[1][-1], args[1][:-1]
    if r:
      retval = make_constant(retval)
    return r, ("Return", retval)

  my_contract_dict = dict()
  my_contract_dict.update(zip(BINOPS,
                              [_two_item for _ in BINOPS]))
  my_contract_dict.update(zip(UNOPS,
                              [_one_item for _ in UNOPS]))
  my_contract_dict.update(zip(NON_CONST_UNOPS,
                              [_bad_one_item for _ in NON_CONST_UNOPS]))
  my_contract_dict["Box"]       = _box
  my_contract_dict["Tuple"]     = _tuple
  my_contract_dict["pow"]       = _pow
  my_contract_dict["powi"]      = _pow
  my_contract_dict["Variable"]  = _variable
  my_contract_dict["Return"]    = _return

  n, new_exp = walk(my_expand_dict, my_contract_dict, exp, assigns)
  assert(n in {True, False})
  assert(type(new_exp) is tuple)
  assert(new_exp[0] not in {True, False})

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
