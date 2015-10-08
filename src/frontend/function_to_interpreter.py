#!/usr/bin/env python3

from function_utils import *
import sys as SYS
import random as R
import subprocess

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


def rewrite_interpreter(exp):
    if exp[0] == 'Input':
        return "i{} ".format(exp[1])
    if exp[0] == 'Bound':
        return rewrite_interpreter(GLOBAL_NAMES[exp[1]])
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
        return "{} p2 fsqrt".format(rewrite_interpreter(exp[1]))
    if exp[0] == "ipow":
        c = GOBAL_CONSTANTS_LIST[exp[2][1]][1]
        return "{} p{}".format(rewrite_interpreter(exp[1]), c)
    print("Error rewriting_interpreter '{}'".format(exp))
    SYS.exit(-1)
