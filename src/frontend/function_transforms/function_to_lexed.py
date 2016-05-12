#!/usr/bin/env python3

import ply.lex as lex
import sys


tokens = [
    # Operators
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "BINPOW",
    "BINOP",
    "UNIOP",

    # Assignment
    "EQUALS",

    # Variables
    "NAME",

    # Literals
    "INTEGER",
    "FLOAT",
    "INTERVAL",

    # Deliminators
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "SEMICOLON",
]


# Operators
t_PLUS    = '\+'

t_MINUS   = '-'

t_TIMES   = '\*'

t_DIVIDE  = '/'

t_BINPOW  = '\^'

prefix_binary_operations = ['pow']
t_BINOP   = "({})".format(")|(".join(prefix_binary_operations))

unary_operations = ['abs', 'cos', 'exp', 'log', 'sin', 'tan', 'sqrt']
t_UNIOP   = "({})".format(")|(".join(unary_operations))




# Assignment
t_EQUALS  = r'='




# Variables
def t_NAME(t):
    r'([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*'
    if t.value in prefix_binary_operations:
        t.type = 'BINOP'
    elif t.value in unary_operations:
        t.type = 'UNIOP'
    elif t.value == 'interval':
        t.type = 'INTERVAL'
    else:
        t.type = 'NAME'

    return t




# Literals
r_float     = ''.join((r'(',                 # match all floats
                       r'(',                 #  match float with '.'
                       r'(',                 #   match a number base
                       r'(\d+\.\d+)',        #    <num.num>
                       r'|',                 #    or
                       r'(\d+\.)',           #    <num.>
                       r'|',                 #    or
                       r'(\.\d+)',           #    <.num>
                       r')',                 #
                       r'(',                 #   then match an exponent
                       r'(e|E)(\+|-)?\d+',   #    <exponent>
                       r')?',                #    optionally
                       r')',                 #
                       r'|',                 #  or
                       r'(',                 #  match float without '.'
                       r'\d+',               #   <num>
                       r'((e|E)(\+|-)?\d+)', #   <exponent>
                       r')',                 #
                       r')'))
t_FLOAT     = r_float

t_INTEGER   = r'\d+'

t_INTERVAL  = 'interval'




# Deliminators
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\['
t_RBRACE    = r'\]'
t_COMMA     = r','
t_SEMICOLON = r';'




# Non-emmitting
t_ignore    = (' \t\n\r')

def t_comment(t):
    r'\#[^\n]*'
    pass

def t_error(t):
    print("Illegal character '{}'".format(t), file=sys.stderr)
    sys.exit(-1)








# Create lexer on call and import
function_lexer = lex.lex() #, optimize=1) #used when stable

# On call run as a util, taking in text and printing the lexed version
if __name__ == "__main__":
    lex.runmain(function_lexer)
