#!/usr/bin/env python3

from lexed_to_parsed import *

import sys

from parsed_passes import BINOPS, UNIOPS


def make_constant(exp, consts):
    ''' Given a constant expression places it in the global const list
    and mutates it to represent that it is a constant '''
    # If the constant value is already in the list, don't recreate it
    try:
        i = consts.index(exp)
    except ValueError:
        i = len(consts)
        consts.append(exp[:])
    exp[0] = 'Const'
    exp[1] = 'Constant_{}'.format(i)
    del exp[2:]


def _lift_constants(exp, consts):
    ''' Given an expression, recursively lifts constants from the expression,
    coalescing neighboring constants. Mutates the expression and returns True
    if the expression was completely constant '''
    if type(exp[0]) is list:
        _lift_constants(exp[0], consts)
        _lift_constants(exp[1], consts)
        return False
    if exp[0] in ['InputInterval', 'Variable', 'Input']:
        return False
    if exp[0] in ['Interval', 'Float', 'Integer']:
        return True
    if exp[0] == 'Return':
        if _lift_constants(exp[1], consts):
            make_constant(exp[1], consts)
        return False
    if exp[0] == 'Assign':
        if _lift_constants(exp[2], consts):
            make_constant(exp[2], consts)
        return False
    if exp[0] in BINOPS:
        first = _lift_constants(exp[1], consts)
        second = _lift_constants(exp[2], consts)
        if first and second:
            return True
        if first:
            make_constant(exp[1], consts)
        if second:
            make_constant(exp[2], consts)
        return False
    if exp[0] in UNIOPS:
        return _lift_constants(exp[1], consts)

    print("Error constant lifting '{}'".format(exp))
    sys.exit(-1)

def lift_constants(exp):
    consts = list()
    _lift_constants(exp, consts)
    return [("Constant_{}".format(i), c) for i,c in enumerate(consts)]
    

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

    exp = parser.parse(data)
    consts = lift_constants(exp)

    print("expresions:")
    while type(exp[0]) is list:
        print(exp[0])
        exp = exp[1]
    print(exp)
    print()
    print("constants:")
    for c in consts:
        print(c)



# On call run as a util, taking in text and printing the constant lifted version
if __name__ == "__main__":
    runmain()
