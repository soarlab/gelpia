#! /usr/bin/env python3

import sys

import ian_utils as iu

from expression_walker import walk
from pass_utils import exp_to_str




def lift_inputs_and_assigns(exp):
    """ Extracts input variables and assignments from an expression """

    # Function local variables
    assigns      = dict() # name -> expression
    used_assigns = set()  # assignments seen in the main exp
    inputs       = dict() # name -> input range
    used_inputs  = set()  # inputs seen in the main exp

    def log(func):
        iu.log(3, lambda : (iu.magenta("lift_inputs_and_assigns: ")
                            + exp_to_str(func())))

    def _input_interval(work_stack, count, exp):
        assert(exp[0] == "InputInterval")
        assert(len(exp) == 3)
        # Here is where implicit inputs should be lifted if/when we decide to
        work_stack.append((True, count, ("ConstantInterval", exp[1], exp[2])))

    def _name(work_stack, count, exp):
        assert(exp[0] == "Name")
        assert(len(exp) == 2)

        if exp[1] in inputs:
            used_inputs.add(exp[1])
            assert(exp[1] not in assigns)
            work_stack.append((True, count, ("Input", exp[1])))
            return

        if exp[1] in assigns:
            used_assigns.add(exp[1])
            assert(exp[1] not in inputs)
            work_stack.append((True,  count, "Variable"))
            work_stack.append((True,  2,     exp[1]))
            work_stack.append((False, 2,     assigns[exp[1]]))
            return

        print("Use of undeclared name: {}".format(exp[1]), file=sys.stderr)
        sys.exit(-1)


    # A leading tuple must be an assign
    while type(exp[0]) is tuple:
        assignment = exp[0]
        assert(assignment[0] == "Assign")
        name = assignment[1]
        if name[0] == "SymbolicConst":
            log(lambda:"Dropping assignment to symbolic constant '{}'"
                 .format(name[1]))
            exp = exp[1]
            continue
        assert(name[0] == "Name")
        val  = assignment[2]
        # Explicit inputs
        if val[0] == "InputInterval":
            assert(name[1] not in inputs)
            inputs[name[1]] = val
            log(lambda : "Found input {} = {}".format(name[1],
                                                          exp_to_str(val)))
        # Assignment to an expression
        else:
            assert(name[1] not in assigns)
            assigns[name[1]] = val
            log(lambda : "Found assign {} = {}".format(name[1],
                                                           exp_to_str(val)))

        # Work on the rest of the expression
        exp = exp[1]


    my_expand_dict = {"InputInterval": _input_interval,
                      "Name":          _name}

    new_exp = walk(my_expand_dict, dict(), exp, assigns)

    # Remove dead inputs
    dead_inputs = set(inputs).difference(used_inputs)
    for k in dead_inputs:
        del inputs[k]
        log(lambda : "Removing dead input {}".format(k))

    # Remove dead assigns
    dead_assigns = set(assigns).difference(used_assigns)
    for k in dead_assigns:
        del assigns[k]
        log(lambda : "Removing dead assign {}".format(k))

    return new_exp, inputs, assigns










def main(argv):
    try:
        from lexed_to_parsed import parse_function
        from pass_utils import get_runmain_input, print_exp
        from pass_utils import print_assigns, print_inputs

        data = get_runmain_input(argv)
        exp = parse_function(data)
        iu.set_log_level(100)
        exp, inputs, assigns = lift_inputs_and_assigns(exp)

        print()
        print()
        print_inputs(inputs)
        print()
        print_assigns(assigns)
        print()
        print_exp(exp)

    except KeyboardInterrupt:
        print("\nGoodbye")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
