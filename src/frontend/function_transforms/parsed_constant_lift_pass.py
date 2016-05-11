#!/usr/bin/env python3

from lexed_to_parsed import *
from parsed_input_lift_pass import *

import sys

from parsed_passes import BINOPS, UNIOPS


def lift_constants(exp, inputs):
    consts = list()

    def make_constant(exp):
        try:
            i = consts.index(exp)
        except ValueError:
            i = len(consts)
            consts.append(exp[:])
        exp[0] = 'Const'
        exp[1] = '{}'.format(i)
        del exp[2:]


    def _lift_constants(exp):
        if type(exp[0]) is list:
            _lift_constants(exp[0])
            _lift_constants(exp[1])
            return False
        if exp[0] in ['InputInterval', 'Variable', 'Input']:
            return False
        if exp[0] in ['Interval', 'Float', 'Integer']:
            return True
        if exp[0] == 'Return':
            if _lift_constants(exp[1]):
                make_constant(exp[1])
            return False
        if exp[0] == 'Assign':
            if _lift_constants(exp[2]):
                make_constant(exp[2])
            return False
        if exp[0] in BINOPS:
            first = _lift_constants(exp[1])
            second = _lift_constants(exp[2])
            if first and second:
                return True
            elif first:
                make_constant(exp[1])
            elif second:
                make_constant(exp[2])
            return False
        if exp[0] in UNIOPS:
            return _lift_constants(exp[1])

        print("Error constant lifting '{}'".format(exp))
        sys.exit(-1)

    _lift_constants(exp)
    return consts




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
