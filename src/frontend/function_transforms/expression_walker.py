
import sys

from pass_utils import BINOPS, UNOPS, ATOMS

def expand_two(work_stack, count, exp):
  assert(len(exp) == 3)
  work_stack.append((True,  count, exp[0]))
  work_stack.append((False, 2,     exp[2]))
  work_stack.append((False, 2,     exp[1]))

def expand_one(work_stack, count, exp):
  assert(len(exp) == 2)
  work_stack.append((True,  count, exp[0]))
  work_stack.append((False, 1,     exp[1]))

def expand_atom(work_stack, count, exp):
  work_stack.append((True, count, exp))

def expand_many(work_stack, count, exp):
  sub_count = len(exp) - 1
  if sub_count == 0:
    work_stack.append((True,  count, (exp[0],)))
    return

  work_stack.append((True,  count, exp[0]))
  for sub in reversed(exp[1:]):
    work_stack.append((False,  sub_count, sub))

def expand_error(work_stack, count, exp):
  print("EXPAND ERROR: {}".format(exp), file=sys.stderr)
  sys.exit(-1)

default_walk_expand_func_dict = dict()
default_walk_expand_func_dict.update(zip(BINOPS, [expand_two  for _ in BINOPS]))
default_walk_expand_func_dict.update(zip(UNOPS,  [expand_one  for _ in UNOPS]))
default_walk_expand_func_dict.update(zip(ATOMS,  [expand_atom for _ in ATOMS]))
default_walk_expand_func_dict["Tuple"]  = expand_two
default_walk_expand_func_dict["Box"]    = expand_many
default_walk_expand_func_dict["Input"]  = expand_atom
default_walk_expand_func_dict["Const"]  = expand_atom
default_walk_expand_func_dict["Return"] = expand_one






def contract_many(work_stack, count, args):
  work_stack.append((True,  count, tuple(args)))

def contract_return(work_stack, count, args):
  assert(args[0] == "Return")
  assert(len(args) == 2)
  return tuple(args)

def contract_error(work_stack, count, exp):
  print("CONTRACT ERROR: {}".format(exp), file=sys.stderr)
  sys.exit(-1)

default_walk_contract_func_dict = dict()
default_walk_contract_func_dict.update(zip(BINOPS, [contract_many for _ in BINOPS]))
default_walk_contract_func_dict.update(zip(UNOPS,  [contract_many for _ in UNOPS]))
default_walk_contract_func_dict.update(zip(ATOMS,  [contract_many for _ in ATOMS]))
default_walk_contract_func_dict["Tuple"]  = contract_many
default_walk_contract_func_dict["Box"]    = contract_many
default_walk_contract_func_dict["Input"]  = contract_many
default_walk_contract_func_dict["Const"]  = contract_many
default_walk_contract_func_dict["Return"] = contract_return






def constant_expand_two(work_stack, count, exp):
  assert(len(exp) == 3)
  work_stack.append((False, 2,     exp[2]))
  work_stack.append((False, 2,     exp[1]))

def constant_expand_one(work_stack, count, exp):
  assert(len(exp) == 2)
  work_stack.append((False, 1,     exp[1]))

def constant_expand_atom(work_stack, count, exp):
  pass

def constant_expand_many(work_stack, count, exp):
  sub_count = len(exp) - 1
  if sub_count == 0:
    return

  for sub in reversed(exp[1:]):
    work_stack.append((False,  sub_count, sub))

constant_walk_expand_func_dict = dict()
constant_walk_expand_func_dict.update(zip(BINOPS, [constant_expand_two  for _ in BINOPS]))
constant_walk_expand_func_dict.update(zip(UNOPS,  [constant_expand_one  for _ in UNOPS]))
constant_walk_expand_func_dict.update(zip(ATOMS,  [constant_expand_atom for _ in ATOMS]))
constant_walk_expand_func_dict["Tuple"]  = constant_expand_two
constant_walk_expand_func_dict["Box"]    = constant_expand_many
constant_walk_expand_func_dict["Input"]  = constant_expand_atom
constant_walk_expand_func_dict["Const"]  = constant_expand_atom
constant_walk_expand_func_dict["Return"] = constant_expand_one





def constant_contract_return(work_stack, count, args):
  assert(args[0] == "Return")
  assert(len(args) == 2)
  return True

constant_walk_contract_func_dict = dict()
constant_walk_contract_func_dict["Return"] = constant_contract_return






def walk(expand_dict, contract_dict, exp, assigns=None):
  seen_assigns = set()

  def _e_variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 2)
    assert(exp[1] in assigns)
    if exp[1] not in seen_assigns:
      seen_assigns.add(exp[1])
      work_stack.append((True,  count, exp[0]))
      work_stack.append((True,  2,     exp[1]))
      work_stack.append((False, 2,     assigns[exp[1]]))
    else:
      work_stack.append((True, count, exp))


  def _c_variable(work_stack, count, args):
    assert(args[0] == "Variable")
    assert(len(args) == 3)
    assert(args[1] in assigns)
    assigns[args[1]] = args[2]
    work_stack.append((True, count, tuple(args[0:2])))


  if "Variable" not in expand_dict:
    expand_dict["Variable"] = _e_variable

  if "Variable" not in contract_dict:
    contract_dict["Variable"] = _c_variable

  return _walk(default_walk_expand_func_dict, expand_dict,
               default_walk_contract_func_dict, contract_dict,
               exp, assigns)


def no_mut_walk(expand_dict, exp, assigns=None):
  seen_assigns = set()

  def _e_variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 2)
    assert(exp[1] in assigns)
    if exp[1] not in seen_assigns:
      seen_assigns.add(exp[1])
      work_stack.append((False, 2,     assigns[exp[1]]))

  if "Variable" not in expand_dict:
    expand_dict["Variable"] = _e_variable

  return _walk(constant_walk_expand_func_dict, expand_dict,
               constant_walk_contract_func_dict, dict(),
               exp, assigns)


def _walk(default_expand_dict, expand_dict,
          default_contract_dict, contract_dict,
          exp, assigns):
  expand_err   = expand_dict.get("ERROR", expand_error)
  contract_err = contract_dict.get("ERROR", contract_error)

  work_stack = [(False, 0, exp)]
  while len(work_stack) > 0:
    done, count, exp = work_stack.pop()

    # Expand
    if done == False:
      tag = exp[0]
      if tag in expand_dict:
        expand_func = expand_dict[tag]
      else:
        expand_func = default_expand_dict.get(tag, expand_err)
      expand_func(work_stack, count, exp)



    # Contract all args
    elif work_stack[-1][0] == False:
      index = None
      for index in range(2, count+2):
        temp = work_stack[-index]
        assert(index == count or temp[1] == count)
        if temp[0] == True:
          break

      assert(index is not None)
      assert(index != count+1)
      work_stack.insert(-(index-1), (True, count, exp))



    # Contract this op
    else:
      args = [exp]
      for _ in range(count-1):
        new_done, new_count, new_exp = work_stack.pop()
        assert(new_done == True)
        assert(new_count == count)
        args.append(new_exp)

      op_done, op_count, op = work_stack.pop()
      assert(op_done == True)
      args.append(op)
      args.reverse()

      if op in contract_dict:
        contract_func = contract_dict[op]
      else:
        contract_func = default_contract_dict.get(op, contract_err)

      retval = contract_func(work_stack, op_count, args)
      if retval != None:
        return retval
