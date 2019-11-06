#!/usr/bin/env python3

import os.path as path
import re
import subprocess
import sys

import ian_utils as iu

try:
    from gelpia import bin_dir
except:
    print("gelpia not found, gaol_repl must be in your PATH\n")
    bin_dir = ""

from pass_utils import BINOPS, UNOPS, expand
from output_flatten import flatten




def div_by_zero(exp, inputs, assigns, consts):
    # This pass is currently unused.
    # Should we get rid of it?

    query_proc = subprocess.Popen(path.join(bin_dir, 'gaol_repl'),
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    root = exp
    bad_exp = None

    def gaol_eval(exp):
        flat_exp = flatten(exp, inputs, assigns, consts)
        query_proc.stdin.write('{}\n'.format(flat_exp))
        result = query_proc.stdout.readline()
        try:
            match = re.match("[<\[]([^,]+),([^>\]]+)[>\]]", result)
            l = float(match.group(1))
            r = float(match.group(2))
        except:
            print("Fatal error in gaol_eval")
            print("       query was: '{}'".format(flat_exp))
            print(" unable to match: '{}'".format(result))
            sys.exit(-1)
        return l,r

    def contains_zero(exp):
        l,r = gaol_eval(exp)
        return l<=0 and 0<=r

    def less_than_zero(exp):
        l,r = gaol_eval(exp)
        return l<0

    def _div_by_zero(exp):
        nonlocal bad_exp
        typ = exp[0]
        if typ in {'Float', 'Integer', 'ConstantInterval',
                   'InputInterval', 'Input', 'Symbol', "SymbolicConst"}:
            return False

        if typ == '/':
            retval = (contains_zero(exp[2]) or
                      _div_by_zero(exp[1]) or
                      _div_by_zero(exp[2]))
            if retval:
                bad_exp = exp
            return retval

        if typ == "powi":
            temp = False
            if less_than_zero(exp[2]):
                temp = contains_zero(exp[1])
            retval = temp or _div_by_zero(exp[1]) or _div_by_zero(exp[2])
            if retval:
                bad_exp = exp
            return retval

        if typ == "pow":
            temp = False
            e = expand(exp[2], assigns, consts)
            assert(e[0] == "Integer")
            if int(e[1]) < 0:
                temp = contains_zero(exp[1])
            retval = temp or _div_by_zero(exp[1])
            if retval:
                bad_exp = exp
            return retval

        if typ in BINOPS:
            return _div_by_zero(exp[1]) or _div_by_zero(exp[2])

        if typ in UNOPS.union({"Return"}):
            return _div_by_zero(exp[1])

        if typ in {"Variable"}:
            return _div_by_zero(assigns[exp[1]])

        if typ in {"Const"}:
            return _div_by_zero(consts[exp[1]])

        print("div_by_zero error unknown: '{}'".format(exp))
        sys.exit(-1)

    result = _div_by_zero(exp)
    query_proc.communicate()
    return (result, bad_exp)







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
        _, exp, consts = lift_consts(exp, inputs, assigns)
        iu.set_log_level(100)
        has_div_zero, bad_exp = div_by_zero(exp, inputs, assigns, consts)

        print()
        print()
        print_inputs(inputs)
        print()
        print_assigns(assigns)
        print()
        print_consts(consts)
        print()
        print_exp(exp)
        print()
        print("Does expression divide by zero: {}".format(has_div_zero))
        if has_div_zero:
            print()
            print("offending exp:")
            print(bad_exp)

    except KeyboardInterrupt:
        print("\nGoodbye")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
