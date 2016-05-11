#!/usr/bin/env python3

from lexed_to_parsed import *
from lifted_to_rust import *

import sys

from parsed_passes import BINOPS, UNIOPS


def flatten(root, exp, inputs, consts):

    def _flatten(exp):
        if type(exp[0]) is list:
            return _flatten(exp[1])
        if exp[0] in ['InputInterval', 'Interval']:
            l = _flatten(exp[1]).replace('[','').replace(']','')
            r = _flatten(exp[2]).replace('[','').replace(']','')
            return "[{}, {}]".format(l,r)
        if exp[0] in ['Float', 'Integer']:
            return "[{}]".format(exp[1])
        if exp[0] in ['Variable', 'Input']:
            tlist = [t for t in inputs if t[0] == exp[1]]
            if len(tlist) == 1:
                return tlist[0][1]
            else:
                return _flatten(lookup(exp[1]))
        if exp[0] == 'Const':
            return consts[int(exp[1])]
        if exp[0] == 'Return':
            return _flatten(exp[1])
        if exp[0] in ops:
            return "({}{}{})".format(_flatten(exp[1]), ops[exp[0]], _flatten(exp[2]))
        if exp[0] in funcs:
            return "{}({})".format(funcs[exp[0]], _flatten(exp[1]))
        if exp[0] == 'abs':
            return "abs({})".format(_flatten(exp[1]))
        if exp[0] == 'Neg':
            return "-({})".format(_flatten(exp[1]))
        if exp[0] == 'pow':
            return "powi({},{})".format(_flatten(exp[1]), _flatten(exp[2]))
        if exp[0] == 'cpow':
            return "pow({},{})".format(_flatten(exp[1]), _flatten(exp[2]))
        if exp[0] == "ipow":
            c = consts[int(exp[2][1])]
            return "pow({},{})".format(_flatten(exp[1]), c)
        if exp[0] == "sqrt":
            return"sqrt({})".format(_flatten(exp[1]))
        print("Error flattening '{}'".format(exp))
        sys.exit(-1)

    def lookup(var):
        tmp = root
        while tmp[0] != 'Return':
            assign = tmp[0]
            new_var = assign[1][1]
            if new_var == var:
                return assign[2]
            tmp = tmp[1]
        print("Invalid lookup: {}\nIn:{}\n".format(var, root))
        sys.exit(-1)

    return _flatten(exp)

                                
                                

def runmain():
    ''' Wrapper to allow constant lifter to run with direct
    command line input '''
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            data = f.read()
    except IndexError:
        sys.stdout.write('Reading from standard input (type EOF to end):\n')
        data = sys.stdin.read()

    exp = function_parser.parse(data)
    inputs = lift_inputs(exp)
    consts = lift_constants(exp, inputs)
    flattened = flatten(exp, exp, inputs, consts)

    print("flattened:")
    print(flattened)
    print()
    print("expresions:")
    while type(exp[0]) is list:
        print(exp[0])
        exp = exp[1]
    print(exp)
    print()
    print("inputs:")
    for i in inputs:
        print(i)
    print()
    print("constants:")
    for c in consts:
        print(c)

# On call run as a util, taking in text and printing the constant lifted version
if __name__ == "__main__":
    runmain()
