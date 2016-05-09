#!/usr/bin/env python3

from function_to_lexed import *

import ply.yacc as yacc
import sys


# this list is tuples of (name, binding) for all bound
# variables in the function.
GLOBAL_BINDINGS = dict()
INFERRED_COUNT = 0

def p_function_assign(t):
    '''function : VARIABLE EQUALS expression SEMICOLON function'''
    # make sure this variable being assigned to has not alreaady been used as
    # free
    if t[1] in GLOBAL_BINDINGS.keys():
        if GLOBAL_BINDINS[t[1]] == None:
            print("Error free varaible assigned to: Free var '{}'".format(t[1]),
                  file=sys.stderr)
        else:
            print("Error double assignment to: Bound var '{}'".format(t[1]),
                  file=sys.stderr)
        sys.exit(-1)

    # set the global bookeeping variables
    GLOBAL_BINDINGS[t[1]] = t[3]

    # Returns ['Assign', ['Variable, Name, Binding, Next]]
    t[0] = ['Assign', ['Variable', t[1]], t[3], t[5]]

    
def p_function_end(t):
    '''function : expression
                | expression SEMICOLON'''
    # Returns ['Return', expression]
    t[0] = ['Return', t[1]]

    
def p_expression(t):
    '''expression : expression PLUS term
                  | expression MINUS term'''
    # Returns [operator, lhs, rhs]
    t[0] = [t[2], t[1], t[3]]

    
def p_expression_passthrough(t):
    '''expression : term'''
    t[0] = t[1]

    
def p_term(t):
    '''term : term TIMES uniop
            | term DIVIDE uniop'''
    # Returns [operator, lhs, rhs]
    t[0] = [t[2], t[1], t[3]]

    
def p_term_passthrough(t):
    '''term : uniop'''
    t[0] = t[1]

    
def p_uniop_neg(t):
    '''uniop : MINUS base'''
    # Returns ['Neg', value]
    t[0] = ['Neg', t[2]]

    
def p_uniop_passthrough(t):
    '''uniop : base'''
    t[0] = t[1]

    
def p_base_passthrough(t):
    '''base : name
            | const
            | group
            | func'''
    t[0] = t[1]

    
def p_name(t):
    '''name : VARIABLE'''
    # if the name has not already been bound it must be free
    val = GLOBAL_BINDINGS.get(t[1], -1)
    if (val == -1):
        GLOBAL_BINDINGS[t[1]] = None
        val = None    
    if (val == None or type(val) == tuple):
        t[0] = ['Input', t[1]]
    else:
        t[0] = ['Variable', t[1]]

        
def p_const_passthrough(t):
    '''const : number
             | interval'''
    t[0] = t[1]

    
def p_number_integer(t):
    '''number : INTEGER'''
    # Returns ['Integer', value]
    t[0] = ['Integer', t[1]]

    
def p_number_float(t):
    '''number : FLOAT'''
    # Returns ['Float', value]
    t[0] = ['Float', t[1]]

    
def p_interval(t):
    '''interval : INTERVAL LPAREN number COMMA number RPAREN'''
    # Returns ['Interval', value content, value content]
    if (t[3][1] == t[5][1]):
        t[0] = ['Interval', t[3][1], t[5][1]]
    else:
        global INFERRED_COUNT
        new_name = "inferred_variable_{}".format(INFERRED_COUNT)
        INFERRED_COUNT += 1
        GLOBAL_BINDINGS[new_name] = (t[3][1], t[5][1])
        t[0] = ['Input', new_name]

    
def p_group_passthrough(t):
    '''group : LPAREN expression RPAREN'''
    t[0] = t[2]

    
def p_func_uniop(t):
    '''func : UNIOP LPAREN expression RPAREN'''
    # Returns [operator, value]
    t[0] = [t[1], t[3]]

    
def p_func_binop(t):
    '''func : BINOP LPAREN expression COMMA expression RPAREN'''
    if t[1] == 'pow' and t[5][0] == 'Integer':
        # special case for integer power
        # Returns ['ipow', base, exponent]
        t[0] = ['ipow', t[3], t[5]]
    else:
        # Returns [operator, value, value]
        t[0] = [t[1], t[3], t[5]]


def p_error(t):
    print("Syntax error at '{}'".format(t))




# Create parser on call and import
parser = yacc.yacc(debug=0, write_tables=0)

def runmain_parser(parser):
    ''' Wrapper to allow parser to run with direct command line input '''
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            data = f.read()
    except IndexError:
        sys.stdout.write('Reading from standard input (type EOF to end):\n')
        data = sys.stdin.read()

    exp = parser.parse(data)

    print(GLOBAL_BINDINGS)
    print()
    print(exp)
    
# On call run as a util, taking in text and printing the parsed version
if __name__ == "__main__":
    runmain_parser(parser)
