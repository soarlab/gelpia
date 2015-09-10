#!/usr/bin/env python3

from function_utils import *
import sys as SYS
import random as R
import subprocess

ops_post = {
    '+'      : '+',
    '-'      : '-',
    '*'      : '*',
    '/'      : '/',
    'pow'    : 'p',
}

funcs_post = {
    'sin'    : 'sin',
    'cos'    : 'cos',
    'tan'    : 'tan',
    'exp'    : 'exp',
    'log'    : 'log',
    'Neg'    : 'neg',
}


def rewrite_post(exp):
    if exp[0] == 'Input':
        return "i{} ".format(exp[1])
    if exp[0] == 'Bound':
        return rewrite_post(GLOBAL_NAMES[exp[1]])
    if exp[0] == 'Const':
        return "c{} ".format(exp[1])
    if exp[0] in ['Return']:
        return rewrite_post(exp[1])
    if exp[0] == 'Assign':
        return rewrite_post(exp[3])
    if exp[0] in ops_post:
        return "{} {} o{}".format(rewrite_post(exp[1]),
                                 rewrite_post(exp[2]),
                                 ops_post[exp[0]])
    if exp[0] in funcs_post:
        return "{} f{}".format(rewrite_post(exp[1]),
                              funcs_post[exp[0]])
    if exp[0] == 'abs':
        return "{} p2 fsqrt".format(rewrite_post(exp[1]))
    if exp[0] == "ipow":
        c = GOBAL_CONSTANTS_LIST[exp[2][1]][1]
        return "{} p{}".format(rewrite_post(exp[1]), c)
    print("Error rewriting_post '{}'".format(exp))
    SYS.exit(-1)

ops = {
    '+'      : '+',
    '-'      : '-',
    '*'      : '*',
    '/'      : '/',
}

funcs = {
    'sin'    : 'sin',
    'cos'    : 'cos',
    'tan'    : 'tan',
    'exp'    : 'exp',
    'log'    : 'log',
}

def rewrite(exp):
    if exp[0] == 'Float':
        return "{}".format(exp[1])
    if exp[0] == 'Interval':
        return "[{}, {}]".format(exp[1], exp[2])    
    if exp[0] == 'Input':
        return "_x[{}]".format(exp[1])
    if exp[0] == 'Bound':
        return rewrite(GLOBAL_NAMES[exp[1]])
    if exp[0] == 'Const':
        return "_c[{}]".format(exp[1])
    if exp[0] in ['Return']:
        return rewrite(exp[1])
    if exp[0] == 'Assign':
        return rewrite(exp[3])
    if exp[0] in ops:
        return "({} {} {})".format(rewrite(exp[1]),
                                   ops[exp[0]],
                                   rewrite(exp[2]))
    if exp[0] in funcs:
        return "{}({})".format(funcs[exp[0]],
                               rewrite(exp[1]))
    if exp[0] == 'abs':
        return "(sqrt(pow({}, 2)))".format(rewrite(exp[1]))
    if exp[0] == 'Neg':
        return "-({})".format(rewrite(exp[1]))
    if exp[0] == 'pow':
        return "powi({}, {})".format(rewrite(exp[1]), rewrite(exp[2]))
    if exp[0] == "ipow":
        c = GOBAL_CONSTANTS_LIST[exp[2][1]][1]
        return "{pow({}, {})".format(rewrite(exp[1]), c)
    print("Error rewriting '{}'".format(exp))
    SYS.exit(-1)

def trans_const():
    consts = list()
    for expr in GLOBAL_CONSTANTS_LIST:
        consts.append(rewrite(expr).replace("powi", "pow"))
    return consts
        
def translate(data):
    function = """extern crate gr;
use gr::*;

#[no_mangle]
pub extern "C"
fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {
"""
    
    exp = parser.parse(data)
    lift_constants(exp)
    constants = "|".join(trans_const())

#    input_strings = ["    let v = vec!["]
#    input_strings.extend(['GI::new_d(1.0, 1.0), ' for i
#                          in GLOBAL_FREE_NAMES_SET])
#    if len(input_strings) != 1:
#        input_strings[-1] = input_strings[-1][0:-2]
#    input_strings.append('];')
#    print("".join(input_strings))

    part = rewrite_post(exp)
    part = ', '.join(part.split())
    
#    print('    let f = FuncObj::new(&consts, ')
#    print('                         &"{}".to_string());'.format(part))
    function += '    {}'.format(rewrite(exp))

#    print('    let real = f.call(&v).to_string();')
#    print('    assert!(real == expected, "real = {}, expected = {}", real, expected);')
    function += '\n}\n'
    
    return (function, constants, part)
    

def runmain():
    try:
        filename = SYS.argv[1]
        f = open(filename)
        data = f.read()
        f.close()
    except IndexError:
        SYS.stdout.write('Reading from standard input (type EOF to end):\n')
        data = SYS.stdin.read()

    (function, constants, part) = translate(data)
    import random
#    inputs = []
    inputs = [(.001, 1) for i in range(50)]
#    for i in range(50):
#        first = 50*random.random()
#        second = 50*random.random()
#        while second < first:
#            second = 50*random.random()
#        inputs.append((first,second))
    inputs = ["[{}, {}]".format(x[0], x[1]) for x in inputs]
    inputs = "|".join(inputs)
    with open("src/func/src/lib.rs", 'w') as f:
        f.write(function)
    subprocess.call(['target/release/serial', '-c', constants, '-f', part, '-i', inputs])


if __name__ == "__main__":
    runmain()
