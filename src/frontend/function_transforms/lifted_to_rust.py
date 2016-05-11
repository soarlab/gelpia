#!/usr/bin/env python3

from parsed_constant_lift_pass import *
from parsed_input_lift_pass import *

import sys


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

def rewrite_rust(exp, consts, inputs):

    def _rewrite_rust(exp):
        if type(exp[0]) is list:
            return "{}\n{}".format(_rewrite_rust(exp[0]),
                                   _rewrite_rust(exp[1]))
        if exp[0] in ['Float', 'Integer']:
            return "[{}]".format(exp[1])
        if exp[0] in ['Interval', 'InputInterval']:
            l = _rewrite_rust(exp[1]).replace('[','').replace(']','')
            r = _rewrite_rust(exp[2]).replace('[','').replace(']','')
            return "[{},{}]".format(l,r)
        if exp[0] == 'Input':
            return "_x[{}]".format(input_names.index(exp[1]))
        if exp[0] == 'Variable':
            return exp[1]
        if exp[0] == 'Const':
            return "_c[{}]".format(const_names.index(exp[1]))
        if exp[0] in ['Return']:
            return _rewrite_rust(exp[1])
        if exp[0] == 'Assign':
            return "let {} = {};".format(exp[1][1], _rewrite_rust(exp[2]))
        if exp[0] in ops:
            return "({}{}{})".format(_rewrite_rust(exp[1]), ops[exp[0]], _rewrite_rust(exp[2]))
        if exp[0] in funcs:
            return "{}({})".format(funcs[exp[0]], _rewrite_rust(exp[1]))
        if exp[0] == 'abs':
            return "abs({})".format(_rewrite_rust(exp[1]))
        if exp[0] == 'Neg':
            return "-({})".format(_rewrite_rust(exp[1]))
        if exp[0] == 'pow':
            return "powi({},{})".format(_rewrite_rust(exp[1]), _rewrite_rust(exp[2]))
        if exp[0] == 'cpow':
            return "pow({},{})".format(_rewrite_rust(exp[1]), _rewrite_rust(exp[2]))
        if exp[0] == "ipow":
            c = consts[const_names.index(exp[2][1])][1][1]
            return "pow({},{})".format(_rewrite_rust(exp[1]), c)
        if exp[0] == "sqrt":
            return"sqrt({})".format(_rewrite_rust(exp[1]))
        print("Error rewriting '{}'".format(exp))
        sys.exit(-1)

    input_names = [tup[0] for tup in inputs]
    const_names = [tup[0] for tup in consts]
    return _rewrite_rust(exp)


def trans_const_r(expr):
    '''expr is a constant. We need to replace abs with sqrt(pow( '''
    if type(expr) != list:
        return expr
    if expr[0] == 'powi':
        return ['pow', trans_const_r(expr[1])]
    return [trans_const_r(e) for e in expr]
    

def trans_const(consts):
    new_consts = list()
    for tup in consts:
        new_consts.append((tup[0], rewrite_rust(trans_const_r(tup[1]), list(), list())))
    return new_consts


def translate_rust(exp, consts, inputs):
    function = ["extern crate gr;",
                "use gr::*;",
                "",
                "#[no_mangle]",
                "pub extern \"C\"",
                "fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {"]

    function.append('    {}'.format(rewrite_rust(exp, consts, inputs)))
    function.extend(["}", ""])
    function = '\n'.join(function)
    new_inputs = trans_const(inputs)
    new_consts = trans_const(consts)
    return (function, new_inputs, new_consts)
    

def runmain():
    ''' Wrapper to allow translater to run with direct command line input '''
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            data = f.read()
    except IndexError:
        sys.stdout.write('Reading from standard input (type EOF to end):\n')
        data = sys.stdin.read()
    exp = parser.parse(data)
    lift_constants(exp)

    exp = parser.parse(data)
    inputs = lift_inputs(exp)
    consts = lift_constants(exp)
    
    function, new_inputs, new_consts = translate_rust(exp, consts, inputs)
    print("function:")
    print(function)
    print()
    print("constants:")
    for c in new_consts:
        print(c)
    print()
    print("inputs:")
    for i in new_inputs:
        print(i)



if __name__ == "__main__":
    runmain()
