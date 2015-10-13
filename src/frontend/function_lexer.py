#!/usr/bin/env python3

import ply.lex as LEX
import sys as SYS

prefix_binary_functions = [
    'pow',
]

prefix_unary_functions = [
    'abs',
    'cos',
    'exp',
    'log',
    'sin',
    'tan',
    'sqrt'
]

tokens = [
    # Operators
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'BINOP',
    'UNIOP',

    # Assignment
    'EQUALS',

    # Variables
    'VARIABLE',

    # Literals
    'INTEGER',
    'FLOAT',
    'INTERVAL',

    # Deliminators
    'LPAREN',
    'RPAREN',
    'COMMA',
    'SEMICOLON',
]

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_BINOP  = "({})".format(")|(".join(prefix_binary_functions))
t_UNIOP  = "({})".format(")|(".join(prefix_unary_functions))
t_EQUALS = r'='

r_float     = ''.join((r'((',                # First match a number base
                       r'(\d+(\.\d*)?)',     #     <num.>, <num.num>
                       r'|',                 #     or
                       r'(\.\d+)',           #     <.num>
                       r')'                  # Then match an exponent
                       r'((e|E)(\+|-)?\d+)', #     <exponent>
                       r'?'                  #     optionally
                       r')'))
t_FLOAT     = r_float

t_INTEGER   = r'\d+'

def t_VARIABLE(t):
    r'([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*'
    if t.value in prefix_binary_functions:
        t.type = 'BINOP'
    elif t.value in prefix_unary_functions:
        t.type = 'UNIOP'
    elif t.value == 'interval':
        t.type = 'INTERVAL'
    else:
        t.type = 'VARIABLE'
    return t



t_INTERVAL  = 'interval'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r","
t_SEMICOLON = r';'
t_ignore    = (' \t\n\r')

def t_comment(t):
    r'\#[^\n]*'
    pass

def t_error(t):
    print("Illegal character '{}'".format(t), file=SYS.stderr)
    SYS.exit(-1)




# Create lexer on call and import
lexer = LEX.lex()

# On call run as a util, taking in text and printing the lexed version
if __name__ == "__main__":
    LEX.runmain(lexer)
