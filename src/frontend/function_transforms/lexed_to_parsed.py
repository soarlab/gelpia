#!/usr/bin/env python3

from function_to_lexed import *
from function_to_lexed import _function_lexer
from pass_manager import *

import ply.yacc as yacc
import sys


precedence = (
  ("left", "PLUS", "MINUS"),
  ("left", "TIMES", "DIVIDE"),
  ("right", "UMINUS"),
  ("right", "INFIX_POW"),
)


def p_function(t):
  ''' function : variable EQUALS expression SEMICOLON function
               | expression
               | expression SEMICOLON '''
  if len(t) == 6:
    t[0] = [["Assign", t[1], t[3]], t[5]]
  elif len(t) == 2 or len(t) == 3:
    t[0] = ["Return", t[1]]
  else:
    print("Internal parse error in p_function")
    sys.exit(-1)


def p_expression(t):
  ''' expression : expression PLUS expression
                 | expression MINUS expression
                 | expression TIMES expression
                 | expression DIVIDE expression
                 | expression INFIX_POW expression
                 | MINUS expression %prec UMINUS 
                 | base'''
  if len(t) == 4:
    if t[2] == '^' and t[3][0] == "Integer":
      t[0] = ["ipow", t[1], t[3]]
    elif t[2] == '^':
      t[0] = ["pow", t[1], t[3]]
    else:
      t[0] = [t[2], t[1], t[3]]
  elif len(t) == 3:
    t[0] = ["Neg", t[2]]
  elif len(t) == 2:
    t[0] = t[1]
  else:
    print("Internal parse error in p_expression")
    sys.exit(-1)


def p_base(t):
  ''' base : symbolic_const
           | variable
           | interval
           | const
           | group
           | func '''
          
  t[0] = t[1]


def p_variable(t):
  ''' variable : NAME '''
  t[0] = ["Variable", t[1]]


def p_interval(t):
  ''' interval : INTERVAL LPAREN   negconst COMMA    negconst RPAREN
               | LBRACE   negconst COMMA    negconst RBRACE
               | INTERVAL LPAREN   negconst RPAREN
               | LBRACE   negconst RBRACE '''
  if len(t) == 7:
    left = t[3]
    right = t[5]
  elif len(t) == 6:
    left = t[2]
    right = t[4]
  elif len(t) == 5:
    left = t[3]
    right = left
  elif len(t) == 4:
    left = t[2]
    right = left
  else:
    print("Internal parse error in p_interval")
    sys.exit(-1)

  if left == right:
    t[0] = ["ConstantInterval", left]
  else:
    t[0] = ["InputInterval", left, right]


def p_negconst(t):
  ''' negconst : MINUS negconst
               | const '''
  if len(t) == 3:
    typ = t[2][0]
    val = t[2][1]
    if val[0] == '-':
      t[0] = [typ, val[1:]]
    else:
      t[0] = [typ, '-'+val]
  elif len(t) == 2:
    t[0] = t[1]
  else:
    print("Internal parse error in p_negconst")
    sys.exit(-1)


def p_const(t):
  ''' const : PLUS const
            | integer
            | float '''
  if len(t) == 3:
    t[0] = t[2]
  elif len(t) == 2:
    t[0] = t[1]
  else:
    print("Internal parse error in p_const")
    sys.exit(-1)


def p_integer(t):
  ''' integer : INTEGER '''
  t[0] = ["Integer", t[1]]


def p_float(t):
  ''' float : FLOAT '''
  t[0] = ["Float", t[1]]


def p_group(t):
  ''' group : LPAREN expression RPAREN '''
  t[0] = t[2]


def p_func(t):
  ''' func : BINOP LPAREN expression COMMA expression RPAREN
           | UNIOP LPAREN expression RPAREN '''
  if len(t) == 7:
    if t[1] == "pow" and t[5][0] == "Integer":
      t[0] = ["ipow", t[3], t[5]]
    else:
      t[0] = [t[1], t[3], t[5]]
  elif len(t) == 5:
    t[0] = [t[1], t[3]]
  else:
    print("Internal parse error in p_func")
    sys.exit(-1)


def p_symbolic_const(t):
  ''' symbolic_const : SYMBOLIC_CONST '''
  t[0] = ["Symbol", t[1]]
  
  
def p_error(t):
  print("Syntax error at '{}'".format(t))
  sys.exit(-1)


_function_parser = yacc.yacc(debug=0, write_tables=1, optimize=1)

def parse_function(text):
  return _function_parser.parse(text, lexer=_function_lexer)








def runmain():
  data = get_runmain_input()
  exp = parse_function(data)

  print_exp(exp)

if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
