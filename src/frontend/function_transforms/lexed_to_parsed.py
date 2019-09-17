#!/usr/bin/env python3

import sys

try:
    import ply.yacc as yacc
except:
    print("PLY must be installed for python3", file=sys.stderr)
    sys.exit(-1)

from function_to_lexed import *
# underscore names are not imported by default
from function_to_lexed import _function_lexer




strip_arc_dict = {
    "arccos"  : "acos",
    "arcsin"  : "asin",
    "arctan"  : "atan",
    "arccosh" : "acosh",
    "argcosh" : "acosh",
    "arcosh"  : "acosh",
    "arcsinh" : "asinh",
    "argsinh" : "asinh",
    "arsinh"  : "asinh",
    "arctanh" : "atanh",
    "argtanh" : "atanh",
    "artanh"  : "atanh",
}
def strip_arc(f):
  """ Normalizes the names of inverse trig functions """
  return strip_arc_dict.get(f, f)


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
        t[0] = (("Assign", t[1], t[3]), t[5])
    elif len(t) == 2 or len(t) == 3:
        t[0] = ("Return", t[1])
    else:
        print("Internal parse error in p_function", file=sys.stderr)
        sys.exit(-1)


def p_expression(t):
    ''' expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | expression INFIX_POW expression
                   | MINUS expression %prec UMINUS
                   | base '''
    if len(t) == 4:
        if t[2] == "^":
            t[0] = ("powi", t[1], t[3])
        else:
            t[0] = (t[2], t[1], t[3])
    elif len(t) == 3:
        t[0] = ("neg", t[2])
    elif len(t) == 2:
        t[0] = t[1]
    else:
        print("Internal parse error in p_expression", file=sys.stderr)
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
    t[0] = ("Name", t[1])


def p_interval(t):
    ''' interval : INTERVAL LPAREN   negconst COMMA    negconst RPAREN
                 | LBRACE   negconst COMMA    negconst RBRACE
                 | INTERVAL LPAREN   negconst RPAREN
                 | LBRACE   negconst RBRACE '''
    if len(t) == 7:
        left  = t[3]
        right = t[5]
    elif len(t) == 6:
        left  = t[2]
        right = t[4]
    elif len(t) == 5:
        left  = t[3]
        right = left
    elif len(t) == 4:
        left  = t[2]
        right = left
    else:
        print("Internal parse error in p_interval", file=sys.stderr)
        sys.exit(-1)

    if float(left[1]) > float(right[1]):
        print("Upside down intervals not allowed: [{}, {}]"
              .format(left[1], right[1]), file=sys.stderr)
        sys.exit(-1)

    if left == right:
        t[0] = ("PointInterval", left)
    else:
        t[0] = ("InputInterval", left, right)


def p_negconst(t):
    ''' negconst : MINUS negconst
                 | const '''
    if len(t) == 3:
        typ = t[2][0]
        val = t[2][1]
        if val[0] == '-':
            t[0] = (typ, val[1:])
        else:
            t[0] = (typ, '-'+val)
    elif len(t) == 2:
        t[0] = t[1]
    else:
        print("Internal parse error in p_negconst", file=sys.stderr)
        sys.exit(-1)


def p_const(t):
    ''' const : integer
              | float '''
    t[0] = t[1]


def p_integer(t):
    ''' integer : INTEGER '''
    t[0] = ("Integer", t[1])


def p_float(t):
    ''' float : FLOAT '''
    t[0] = ("Float", t[1])


def p_group(t):
    ''' group : LPAREN expression RPAREN '''
    t[0] = t[2]


def p_func(t):
    ''' func : BINOP LPAREN expression COMMA expression RPAREN
             | UNOP  LPAREN expression RPAREN '''
    if len(t) == 7:
        if t[1] == "pow":
            t[1] = "powi"
        if t[1] == "sub2_I":
            t[1] = "sub2"
        t[0] = (t[1], t[3], t[5])
    elif len(t) == 5:
        t[0] = (strip_arc(t[1]), t[3])
    else:
        print("Internal parse error in p_func", file=sys.stderr)
        sys.exit(-1)


def p_symbolic_const(t):
    ''' symbolic_const : SYMBOLIC_CONST '''
    if t[1] in SYMBOLIC_CONSTS:
        val = SYMBOLIC_CONSTS[t[1]]
        t[0] = ("ConstantInterval", val[0], val[1])
    else:
        print("Internal parse error in p_symbolic_const")
        sys.exit(-1)


def p_error(t):
    if t:
        print("Syntax error at '{}' (token {})".format(t.value, t),
              file=sys.stderr)
        sys.exit(-1)
    else:
        print("Unexpected end of function", file=sys.stderr)
        sys.exit(-1)







try:
    from gelpia import bin_dir
    _function_parser = yacc.yacc(debug=False, write_tables=True, optimize=True,
                                 outputdir=bin_dir, tabmodule="main_parsetab.py")
except:
    _function_parser = yacc.yacc(debug=False, write_tables=False,
                                 outputdir="./__pycache__")


def parse_function(text):
    return _function_parser.parse(text, lexer=_function_lexer)


if __name__ == "__main__":
  try:
    from pass_utils import *
    data = get_runmain_input()
    exp = parse_function(data)
    print_exp(exp)
  except KeyboardInterrupt:
    print("\nGoodbye")
