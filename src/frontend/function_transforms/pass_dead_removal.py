#!/usr/bin/env python3

import sys

import ian_utils as iu

from expression_walker import no_mut_walk
from pass_utils import exp_to_str




def dead_removal(exp, inputs, assigns, consts=None):
    # Is this pass still needed? list_inputs_and_assigns cleans up after itself
    # and consts are only made when they are used

    # Function local variables
    used_inputs = set()
    used_assigns = set()
    used_consts = set()

    def log(func):
        iu.log(3, lambda : iu.cyan("dead_removal: ") + exp_to_str(func()))

    def _variable(work_stack, count, exp):
        assert(exp[0] == "Variable")
        assert(len(exp) == 2)
        assert(exp[1] in assigns)
        if exp[1] not in used_assigns:
            used_assigns.add(exp[1])
            work_stack.append((False, 2, assigns[exp[1]]))

    def _input(work_stack, count, exp):
        assert(exp[0] == "Input")
        assert(len(exp) == 2)
        assert(exp[1] in inputs)
        used_inputs.add(exp[1])

    def _const(work_stack, count, exp):
        assert(exp[0] == "Const")
        assert(len(exp) == 2)
        assert(exp[1] in consts)
        used_consts.add(exp[1])


    my_expand_dict = {"Variable": _variable,
                      "Input": _input,
                      "Const": _const}

    no_mut_walk(my_expand_dict, exp, assigns)

    new_inputs = dict()
    for k in inputs:
        if k in used_inputs:
            new_inputs[k] = inputs[k]
        else:
            log(lambda:"Dropping unused input: '{}'".format(k))

    new_assigns = dict()
    for k in assigns:
        if k in used_assigns:
            new_assigns[k] = assigns[k]
        else:
            log(lambda:"Dropping unused assign: '{}'".format(k))

    if consts == None:
        return new_inputs, new_assigns

    new_consts = dict()
    for k in consts:
        if k in used_consts:
            new_consts[k] = consts[k]
        else:
            log(lambda:"Dropping unused const: '{}'".format(k))

    return new_inputs, new_assigns, new_consts










def main(argv):
    try:
        from lexed_to_parsed import parse_function
        from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
        from pass_simplify import simplify
        from pass_lift_consts import lift_consts
        from pass_utils import get_runmain_input, print_exp
        from pass_utils import print_assigns, print_inputs, print_consts

        data = get_runmain_input(argv)
        exp = parse_function(data)
        exp, inputs, assigns = lift_inputs_and_assigns(exp)
        exp = simplify(exp, inputs, assigns)
        e, exp, consts = lift_consts(exp, inputs, assigns)
        iu.set_log_level(100)
        dead_removal(exp, inputs, assigns, consts)

        print()
        print()
        print_inputs(inputs)
        print()
        print_assigns(assigns)
        print()
        print_consts(consts)
        print()
        print_exp(exp)

    except KeyboardInterrupt:
        print("\nGoodbye")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
