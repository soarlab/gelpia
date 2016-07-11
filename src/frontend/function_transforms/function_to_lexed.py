#!/usr/bin/env python3

import ply.lex as lex
import sys


tokens = [
  # Infix Operators
  "PLUS",
  "MINUS",
  "TIMES",
  "DIVIDE",
  "INFIX_POW",

  # Prefix operators
  "BINOP",
  "UNIOP",

  # Variables
  "NAME",

  # Assignment
  "EQUALS",

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




# Infix Operators
t_PLUS      = '\+'
t_MINUS     = '-'
t_TIMES     = '\*'
t_DIVIDE    = '/'
t_INFIX_POW = '\^'


# Prefix operators
BINOPS  = {"pow"}
t_BINOP = "({})".format(")|(".join(BINOPS))

UNIOPS  = {"abs", "cos", "exp", "log", "sin", "tan", "sqrt",
           "arccos", "arcsin", "arctan", "acos", "asin", "atan"}

t_UNIOP = "({})".format(")|(".join(UNIOPS))


# Variables
def t_NAME(t):
  '([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*'
  if t.value in BINOPS:
    t.type = "BINOP"
  elif t.value in UNIOPS:
    t.type = "UNIOP"
  elif t.value in {"interval"}:
    t.type = "INTERVAL"
  else:
    t.type = "NAME"

  return t


# Assignment
t_EQUALS = '='


# Literals
t_FLOAT    = ('('                 # match all floats
              '('                 #  match float with '.'
              '('                 #   match a number base
              '(\d+\.\d+)'        #    <num.num>
              '|'                 #    or
              '(\d+\.)'           #    <num.>
              '|'                 #    or
              '(\.\d+)'           #    <.num>
              ')'                 #
              '('                 #   then match an exponent
              '(e|E)(\+|-)?\d+'   #    <exponent>
              ')?'                #    optionally
              ')'                 #
              '|'                 #  or
              '('                 #  match float without '.'
              '\d+'               #   <num>
              '((e|E)(\+|-)?\d+)' #   <exponent>
              ')'                 #
              ')')
t_INTEGER  = '\d+'
t_INTERVAL = 'interval'


# Deliminators
t_LPAREN    = '\('
t_RPAREN    = '\)'
t_LBRACE    = '\['
t_RBRACE    = '\]'
t_COMMA     = ','
t_SEMICOLON = ';'


# Non-emmitting
t_ignore = (' \t\n\r')
def t_comment(t):
  '\#[^\n]*'
  pass

def t_error(t):
  print("Illegal character '{}'".format(t), file =sys.stderr)
  sys.exit(-1)









_function_lexer = lex.lex(debug=0, optimize=1)

def lex_function(text):
  return _function_lexer.lex(text)

if __name__ == "__main__":
  try:
    lex.runmain(_function_lexer)
  except KeyboardInterrupt:
    print("\nGoodbye")
    
