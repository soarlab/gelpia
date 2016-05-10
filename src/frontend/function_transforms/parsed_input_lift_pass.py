#!/usr/bin/env python3

from lexed_to_parsed import *

import sys

from parsed_passes import BINOPS, UNIOPS

def _lift_inputs(exp, inputs, ref=[0]):
    if type(exp[0]) is list:
        if exp[0][0] == 'Assign' and exp[0][2][0] == 'InputInterval':
            inputs.append((exp[0][1][1], exp[0][2]))
            exp[0] = exp[1][0]
            exp[1] = exp[1][1]
            _lift_inputs(exp, inputs)
            return
        else:
            _lift_inputs(exp[0], inputs)    
            _lift_inputs(exp[1], inputs)
            return
    if exp[0] == 'Assign':
        _lift_inputs(exp[2], inputs)
        return
    if exp[0] == 'InputInterval':
        interval = exp[:]
        exp[0] = 'Input'
        exp[1] = 'Implicit_Input_{}'.format(ref[0])
        del exp[2]
        inputs.append((exp[1], interval))
        return
    if exp[0] in UNIOPS + ['Return']:
        _lift_inputs(exp[1], inputs)
        return
    if exp[0] == 'Assign':
        if exp[2][0] == 'InputInterval':
            exp[1][0] = 'Input'
        else:
            _lift_inputs(exp[2], inputs)
        return
    if exp[0] in BINOPS:
        _lift_inputs(exp[1], inputs)
        _lift_inputs(exp[2], inputs)
        return
    if exp[0] == 'Variable':
        if exp[1] in [i[0] for i in inputs]:
            exp[0] = 'Input'
        return
    if exp[0] in ['Interval', 'Float', 'Integer']:
        return

    print("Error input lifting '{}'".format(exp))
    sys.exit(-1)
        
def lift_inputs(exp):
    inputs = list()
    _lift_inputs(exp, inputs)
    return inputs

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
    inputs = lift_inputs(exp)

    while type(exp[0]) is list:
        print(exp[0])
        exp = exp[1]
    print(exp)
    print()
    for i in inputs:
        print(i)

# On call run as a util, taking in text and printing the constant lifted version
if __name__ == "__main__":
    runmain()
