#!/usr/bin/env python3

import collections
import os
import re
import subprocess
import sys

import ian_utils as iu

from expression_walker import walk
from pass_utils import BINOPS, UNOPS




def single_assignment(exp, inputs, assigns, consts=None):
    PASSTHROUGH = {
        "Const",
        "ConstantInterval",
        "Float",
        "Input",
        "Integer",
        "PointInterval",
    }
    UNCACHED    = PASSTHROUGH.union({"Tuple", "Variable"})
    TWO_ITEMS   = BINOPS.union({"Tuple"})
    ONE_ITEM    = UNOPS.union({"Return"})


    def cache(exp, hashed=dict()):
        if exp[0] in UNCACHED:
            return exp
        try:
            key = hashed[exp]
            iu.log(5, lambda :iu.cyan("Eliminated redundant subexpression")
                   + ": {}".format(exp))
        except KeyError:
            key = "_expr_"+str(len(hashed))
            hashed[exp] = key
            assigns[key] = exp
        return ("Variable", key)


    def _two_items(work_stack, count, args):
        assert(len(args) == 3)
        left  = cache(args[1])
        right = cache(args[2])
        work_stack.append((True, count, (args[0], left, right)))

    def _one_item(work_stack, count, args):
        assert(len(args) == 2)
        arg = cache(args[1])
        work_stack.append((True, count, (args[0], arg)))

    def _many_items(work_stack, count, args):
        args = [args[0]] + [cache(sub) for sub in args[1:]]
        work_stack.append((True, count, tuple(args)))

    my_contract_dict = dict()
    my_contract_dict.update(zip(BINOPS, [_two_items for _ in BINOPS]))
    my_contract_dict.update(zip(UNOPS,  [_one_item for _ in UNOPS]))
    my_contract_dict["Tuple"] = _two_items
    my_contract_dict["Box"] = _many_items

    exp = walk(dict(), my_contract_dict, exp, assigns)

    return exp







def main(argv):
    try:
        from lexed_to_parsed import parse_function
        from pass_lift_consts import lift_consts
        from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
        from pass_simplify import simplify
        from pass_utils import get_runmain_input, print_exp, print_inputs
        from pass_utils import print_assigns, print_consts

        data = get_runmain_input(argv)
        exp = parse_function(data)
        exp, inputs, assigns = lift_inputs_and_assigns(exp)
        exp = simplify(exp, inputs, assigns)
        e, exp, consts = lift_consts(exp, inputs, assigns)
        iu.set_log_level(100)
        exp = single_assignment(exp, inputs, assigns, consts)

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
    main(sys.argv)
