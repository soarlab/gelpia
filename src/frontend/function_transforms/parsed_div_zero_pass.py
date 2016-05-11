#!/usr/bin/env python3

from lexed_to_parsed import *
from lifted_to_rust import *

from parsed_flatten_pass import *

try:
    from gelpia import bin_dir
except:
    print("gelpia not found, gaol_repl must be in your PATH")
    bin_dir = ""
    
import re
import sys
import subprocess
import os.path as path

from parsed_passes import BINOPS, UNIOPS

def div_by_zero(exp, inputs, consts):
    query_proc = subprocess.Popen(path.join(bin_dir, 'gaol_repl'),
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)
    root = exp
    
    def gaol_eval(exp):
        flat_exp = flatten(root, exp, inputs, consts)
        query_proc.stdin.write('{}\n'.format(flat_exp))
        result = query_proc.stdout.readline()
        try:
            match = re.match("[<\[]([^,]+),([^>\]]+)[>\]]", result)
            l = float(match.group(1))
            r = float(match.group(2))
        except:
            print("query was: {}".format(flat_exp))
            print("unable to match: {}".format(result))
            sys.exit()
        return l,r
    
    def contains_zero(exp):
        l,r = gaol_eval(exp)
        return l<=0 and 0<=r

    def less_than_zero(exp):
        l,r = gaol_eval(exp)
        return l<0
    
    def _div_by_zero(exp):
        if exp[0] == '/':
            return contains_zero(exp[2]) or _div_by_zero(exp[1])
        if type(exp[0]) is list:
            return _div_by_zero(exp[0]) or _div_by_zero(exp[1])
        if exp[0] in ['Float', 'Integer','Interval', 'InputInterval', 'Input', 'Variable', 'Const']:
            return False
        if exp[0] in ['Return']:
            return _div_by_zero(exp[1])
        if exp[0] == 'Assign':
            return _div_by_zero(exp[2])
        if exp[0] in ops:
            return _div_by_zero(exp[1]) or _div_by_zero(exp[2])
        if exp[0] in funcs:
            return _div_by_zero(exp[1])
        if exp[0] == 'abs':
            return _div_by_zero(exp[1])
        if exp[0] == 'Neg':
            return _div_by_zero(exp[1])
        if exp[0] == 'pow':
            if less_than_zero(exp[2]):
                return contains_zero(exp[1])
            return _div_by_zero(exp[1]) or _div_by_zero(exp[2])
        if exp[0] == "ipow":
            c = consts[int(exp[2][1])]
            c = c.replace('[','').replace(']','')
            if int(c) < 0:
                return contains_zero(exp[1])
            return _div_by_zero(exp[1]) or _div_by_zero(exp[2])
        if exp[0] == "sqrt":
            return _div_by_zero(exp[1])
        print("Error rewriting '{}'".format(exp))
        sys.exit(-1)

    input_names = [tup[0] for tup in inputs]
    const_names = [tup[0] for tup in consts]
    result = _div_by_zero(exp)
    query_proc.communicate()
    return result


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
    has_div_zero = div_by_zero(exp, inputs, consts)

    print("divides by zero:")
    print(has_div_zero)
    print()
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
