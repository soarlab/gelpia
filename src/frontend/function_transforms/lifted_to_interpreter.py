#!/usr/bin/env python3

from parsed_to_lifted import *
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

def rewrite_interpreter(exp):
    if exp[0] == 'Input':
        return "i{} ".format(GLOBAL_INPUTS_LIST.index(exp[1]))
    if exp[0] == 'Bound':
        return rewrite_interpreter(GLOBAL_BINDINGS[exp[1]])
    if exp[0] == 'Const':
        return "c{} ".format(exp[1])
    if exp[0] in ['Return']:
        return rewrite_interpreter(exp[1])
    if exp[0] == 'Assign':
        return rewrite_interpreter(exp[3])
    if exp[0] in ops_interpreter:
        return "{} {} o{}".format(rewrite_interpreter(exp[1]),
                                 rewrite_interpreter(exp[2]),
                                 ops_interpreter[exp[0]])
    if exp[0] in funcs_interpreter:
        return "{} f{}".format(rewrite_interpreter(exp[1]),
                              funcs_interpreter[exp[0]])
    if exp[0] == 'abs':
        return "{} fabs".format(rewrite_interpreter(exp[1]))
    if exp[0] == 'sqrt':
        return "{} fsqrt".format(rewrite_interpreter(exp[1]))
    if exp[0] == "ipow":
        c = GOBAL_CONSTANTS_LIST[exp[2][1]][1]
        return "{} p{}".format(rewrite_interpreter(exp[1]), c)
    print("Error rewriting_interpreter '{}'".format(exp))
    sys.exit(-1)


def translate_interp(exp):
    function = ','.join(rewrite_interpreter(exp).split())
    var = GLOBAL_INPUTS_LIST
    const = trans_const()
    return (function, var, const)


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
    lift_constants(exp)
    
    function, var, const = translate_interp(exp)
    print(function)
    print()
    print(list(enumerate(var)))
    print()
    print(list(enumerate(const)))

    
if __name__ == '__main__':
    runmain()
