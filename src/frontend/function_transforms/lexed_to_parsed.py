#!/usr/bin/env python3

from function_to_lexed import *

import ply.yacc as yacc
import sys

# helpers
def parse_compare(l, r):
    if l[0] != r[0] or len(l) != len(r):
        return False
    if len(l) > 1:
        return parse_compare(l[1], r[1])
    return True

def is_integer(t):
    if t[0] == 'Neg':
        return is_integer(t[1])
    if t[0] == 'Integer':
        return True
    return False

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'BINPOW')
    )


def p_function_assign(t):
    '''function : variable EQUALS expression SEMICOLON function'''
    t[0] = [['Assign', t[1], t[3]], t[5]]
    

        
def p_function_end(t):
    '''function : expression
                | expression SEMICOLON'''
    t[0] = ['Return', t[1]]




def p_expression(t):
    '''expression : expression PLUS term
                  | expression MINUS term'''
    t[0] = [t[2], t[1], t[3]]

def p_expression_passthrough(t):
    '''expression : term'''
    t[0] = t[1]




def p_term(t):
    '''term : term TIMES binary_pow
            | term DIVIDE binary_pow'''
    t[0] = [t[2], t[1], t[3]]

def p_term_passthrough(t):
    '''term : binary_pow'''
    t[0] = t[1]




def p_binary_pow(t):
    '''binary_pow : binary_pow BINPOW binary_pow'''
    if is_integer(t[3]):
        t[0] = ['ipow', t[1], t[3]]
    else:
        t[0] = ['pow', t[1], t[3]]

def p_binary_pow_passthrouh(t):
    '''binary_pow : uniop'''
    t[0] = t[1]



def p_uniop_neg(t):
    '''uniop : MINUS base'''
    t[0] = ['Neg', t[2]]

def p_uniop_passthrough(t):
    '''uniop : base'''
    t[0] = t[1]




def p_base_passthrough(t):
    '''base : variable
            | const
            | group
            | func'''
    t[0] = t[1]




def p_name(t):
    '''variable : NAME'''
    t[0] = ['Variable', t[1]]




def p_const_passthrough(t):
    '''const : number
             | interval'''
    t[0] = t[1]




def p_number_neg(t):
    '''number : MINUS number'''
    t[0] = ['Neg', t[2]]

def p_number_pos(t):
    '''number : PLUS number'''
    t[0] = t[2]

def p_number_integer(t):
    '''number : INTEGER'''
    t[0] = ['Integer', t[1]]

def p_number_float(t):
    '''number : FLOAT'''
    t[0] = ['Float', t[1]]




def p_interval_single(t):
    '''interval : INTERVAL LPAREN number RPAREN'''
    t[0] = ['Interval', t[3], t[3]]
        
def p_interval(t):
    '''interval : INTERVAL LPAREN number COMMA number RPAREN'''
    if parse_compare(t[3], t[5]):
        t[0] = ['Interval', t[3], t[5]]
    else:
        t[0] = ['InputInterval', t[3], t[5]]

def p_interval_brace_single(t):
    '''interval : LBRACE number RBRACE'''
    t[0] = ['Interval', t[2], t[2]]
    
def p_interval_brace(t):
    '''interval : LBRACE number COMMA number RBRACE'''
    if parse_compare(t[2], t[4]):
        t[0] = ['Interval', t[2], t[4]]
    else:
        t[0] = ['InputInterval', t[2], t[4]]



        
def p_group_passthrough(t):
    '''group : LPAREN expression RPAREN'''
    t[0] = t[2]




def p_func_uniop(t):
    '''func : UNIOP LPAREN expression RPAREN'''
    t[0] = [t[1], t[3]]

def p_func_prefix_binop(t):
    '''func : BINOP LPAREN expression COMMA expression RPAREN'''
    if t[1] == 'pow' and is_integer(t[5]):
        t[0] = ['ipow', t[3], t[5]]
    else:
        t[0] = [t[1], t[3], t[5]]



        
    
def p_error(t):
    print("Syntax error at '{}'".format(t))
    sys.exit(-1)



# Create parser on call and import
function_parser = yacc.yacc(debug=0, write_tables=0)

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
    while type(exp[0]) is list:
        print(exp[0])
        exp = exp[1]
    print(exp)
    
# On call run as a util, taking in text and printing the parsed version
if __name__ == "__main__":
    runmain_parser(function_parser)
