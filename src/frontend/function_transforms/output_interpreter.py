#!/usr/bin/env python3

from parsed_constant_lift_pass import *
from parsed_input_lift_pass import *

from lifted_to_rust import *

import sys


ops_interpreter = {
    '+'      : '+',
    '-'      : '-',
    '*'      : '*',
    '/'      : '/',
    'pow'    : 'p',
}

funcs_interpreter = {
#    'abs' ommitted due to special handling in rewrite_interpreter
    'cos'    : 'cos',
    'exp'    : 'exp',
    'log'    : 'log',
    'Neg'    : 'neg',
    'sin'    : 'sin',
    'tan'    : 'tan',
}

INT_VARIABLES = None

def rewrite_interpreter(exp, consts, inputs):

    def _rewrite_interpreter(exp):
        if exp[0] == 'Input':
            return "i{} ".format(input_names.index(exp[1]))
        if exp[0] == 'Variable':
            return _rewrite_interpreter(bindings[exp[1]])
        if exp[0] == 'Const':
            return "c{} ".format(exp[1])
        if exp[0] in ['Return']:
            return _rewrite_interpreter(exp[1])
        if exp[0] == 'Assign':
            return _rewrite_interpreter(exp[3])
        if exp[0] in ops_interpreter:
            return "{} {} o{}".format(_rewrite_interpreter(exp[1]),
                                      _rewrite_interpreter(exp[2]),
                                      ops_interpreter[exp[0]])
        if exp[0] in funcs_interpreter:
            return "{} f{}".format(_rewrite_interpreter(exp[1]),
                                   funcs_interpreter[exp[0]])
        if exp[0] == 'abs':
            return "{} fabs".format(_rewrite_interpreter(exp[1]))
        if exp[0] == 'sqrt':
            return "{} fsqrt".format(_rewrite_interpreter(exp[1]))
        if exp[0] == "ipow":
            c = consts[int(exp[2][1])]
            c = c.replace('[','').replace(']','')
            return "{} p{}".format(_rewrite_interpreter(exp[1]), c)
        print("Error rewriting interpreter '{}'".format(exp))
        sys.exit(-1)

    input_names = [tup[0] for tup in inputs]

    bindings = dict()
    while type(exp[0]) is list:
        if exp[0][1][0] == 'Variable':
            bindings[exp[0][1][1]] = exp[0][2]
        exp = exp[1]
    
    return _rewrite_interpreter(exp)


def translate_interp(exp, consts, inputs):
    new_inputs = trans_input(inputs)
    new_consts = trans_const(consts)
    function = ','.join(rewrite_interpreter(exp, new_consts, new_inputs).split())
    return (function, new_inputs, new_consts)


def runmain():
    ''' Wrapper to allow interpreter rewriter to run with direct
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
    consts = lift_constants(exp)
    
    function, iconst = translate_interp(exp, consts, inputs)
    print("function:")
    print(function)
    print()
    print("constants:")
    for c in iconsts:
        print(c)
    print()
    print("inputs:")
    for i in inputs:
        print(i)
    
if __name__ == '__main__':
    runmain()
