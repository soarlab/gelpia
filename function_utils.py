#!/usr/bin/env python3

from function_parser import *
import sys as SYS

# constants used in the expression
GLOBAL_CONSTANTS_LIST = list()

# read only list of supported ops
binops = prefix_binary_functions + ['+', '-', '*', '/', 'ipow']
uniops = prefix_unary_functions + ['Neg']

def make_constant(exp):
    global GLOBAL_CONSTANTS_LIST
    try:
        i = GLOBAL_CONSTANTS_LIST.index(exp)
    except ValueError:
        i = len(GLOBAL_CONSTANTS_LIST)
        GLOBAL_CONSTANTS_LIST.append(exp[:])
    exp[0] = 'Const'
    exp[1] = i
    del exp[2:]
    
def lift_constants(exp):
    if exp[0] in ['Input', 'Variable']:
        return False
    if exp[0] in ['Interval', 'Float', 'Integer']:
        return True
    if exp[0] == 'Return':
        if lift_constants(exp[1]):
            make_constant(exp[1])
        return False
    if exp[0] == 'Assign':
        if lift_constants(exp[2]):
            make_constant(exp[2])
        lift_constants(exp[3])
        return False
    if exp[0] in binops:
        first = lift_constants(exp[1])
        second = lift_constants(exp[2])
        if first and second:
            return True
        if first:
            make_constant(exp[1])
        if second:
            make_constant(exp[2])
        return False
    if exp[0] in uniops:
        return lift_constants(exp[1])
        
    print("Error constant lifting '{}'".format(exp))
    SYS.exit(-1)

def runall(data):
    exp = parser.parse(data)
    lift_constants(exp)
    consts = ["{} : {}".format(i, c) for i, c in
              enumerate(GLOBAL_CONSTANTS_LIST)]
    print("[{}]".format('\n '.join(consts)))
    print(exp)
    

def runmain():
    try:
        filename = SYS.argv[1]
        f = open(filename)
        data = f.read()
        f.close()
    except IndexError:
        SYS.stdout.write('Reading from standard input (type EOF to end):\n')
        data = SYS.stdin.read()

    runall(data)
    
if __name__ == "__main__":
    runmain()
