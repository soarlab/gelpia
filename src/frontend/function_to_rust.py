#!/usr/bin/env python3

from function_utils import *
from function_to_interpreter import *
import sys as SYS
import random as R
import subprocess

ops = {
    '+'      : '+',
    '-'      : '-',
    '*'      : '*',
    '/'      : '/',
}

funcs = {
#   'abs' ommitted due to special handling in rewrite_rust
    'cos'    : 'cos',
    'exp'    : 'exp',
    'log'    : 'log',
    'sin'    : 'sin',
    'tan'    : 'tan',
    'sqrt'   : 'sqrt',
}

VARIABLES = None

def rewrite(exp):
    if exp[0] == 'Float':
        return "[{}]".format(exp[1])
    if exp[0] == 'Interval':
        return "[{},{}]".format(exp[1], exp[2])
    if exp[0] == 'Input':
        if exp[1] not in VARIABLES.keys():
            raise "Unknown variable: {}".format(exp[1])
        return "_x[{}]".format(VARIABLES[exp[1]])
    if exp[0] == 'Bound':
        return rewrite(GLOBAL_NAMES[exp[1]])
    if exp[0] == 'Const':
        return "_c[{}]".format(exp[1])
    if exp[0] in ['Return']:
        return rewrite(exp[1])
    if exp[0] == 'Assign':
        return rewrite(exp[3])
    if exp[0] in ops:
        return "({}{}{})".format(rewrite(exp[1]), ops[exp[0]], rewrite(exp[2]))
    if exp[0] in funcs:
        return "{}({})".format(funcs[exp[0]], rewrite(exp[1]))
    if exp[0] == 'abs':
        return "abs({})".format(rewrite(exp[1]))
    if exp[0] == 'Neg':
        return "-({})".format(rewrite(exp[1]))
    if exp[0] == 'pow':
        return "powi({},{})".format(rewrite(exp[1]), rewrite(exp[2]))
    if exp[0] == 'cpow':
        return "pow({},{})".format(rewrite(exp[1]), rewrite(exp[2]))
    if exp[0] == "ipow":
        c = GOBAL_CONSTANTS_LIST[exp[2][1]][1]
        return "pow({},{})".format(rewrite(exp[1]), c)
    if exp[0] == "sqrt":
        return"sqrt({})".format(rewrite(exp[1]))
    print("Error rewriting '{}'".format(exp))
    SYS.exit(-1)


def trans_const_r(expr):
    '''expr is a constant. We need to replace abs with sqrt(pow( '''
    if type(expr) != list:
        return expr
    if expr[0] == 'powi':
        return ['pow', trans_const_r(expr[1])]
    return [trans_const_r(e) for e in expr]
    

def trans_const():
    consts = list()
    for expr in GLOBAL_CONSTANTS_LIST:
        consts.append(rewrite(trans_const_r(expr)))
    return consts


def translate(data, variables):
    global VARIABLES
    VARIABLES = variables
    function = '\n'.join(["extern crate gr;",
                          "use gr::*;",
                          "",
                          "#[no_mangle]",
                          "pub extern \"C\"",
                          "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {"])
    exp = parser.parse(data)
    lift_constants(exp)
    global GLOBAL_CONSTANTS_LIST
    GLOBAL_CONSTANTS_LIST = trans_const()
    constants = '|'.join(GLOBAL_CONSTANTS_LIST)
    part = rewrite_int(exp, variables)
    part = ','.join(part.split())
    function += '    {}'.format(rewrite(exp))
    function += '\n}\n'
    return (function, constants, part)
    

def runmain():
    ''' Wrapper to allow translater to run with direct command line input '''
    try:
        filename = SYS.argv[1]
        f = open(filename)
        data = f.read()
        f.close()
    except IndexError:
        SYS.stdout.write('Reading from standard input (type EOF to end):\n')
        data = SYS.stdin.read()

    (function, constants, part) = translate(data)
    print("Function: ", function)
    print("Constants: ", constants)
    print("Part: ", part)


if __name__ == "__main__":
    runmain()
