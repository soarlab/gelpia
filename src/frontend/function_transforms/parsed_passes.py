#!/usr/bin/env python3

from lexed_to_parsed import *

import sys

BINOPS = prefix_binary_operations + ['+', '-', '*', '/', 'ipow']
UNIOPS = unary_operations + ['Neg']


from parsed_input_lift_pass import *
from parsed_constant_lift_pass import *


    
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
    print("constants:")
    for c in consts:
        print(c)
    print()
    print("inputs:")
    for i in inputs:
        print(i)

# On call run as a util, taking in text and printing the constant lifted version
if __name__ == "__main__":
    runmain()
