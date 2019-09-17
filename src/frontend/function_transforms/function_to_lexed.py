#! /usr/bin/env python3

import sys

try:
    import ply.lex as lex
except:
    print("PLY must be installed for python3", file=sys.stderr)
    sys.exit(-1)




tokens = [
    # Infix Operators
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "INFIX_POW",

    # Prefix operators
    "BINOP",
    "UNOP",

    # Variables
    "NAME",

    # Assignment
    "EQUALS",

    # Literals
    "INTEGER",
    "FLOAT",
    "INTERVAL",
    "SYMBOLIC_CONST",

    # Deliminators
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "SEMICOLON",
]




# Infix Operators
t_PLUS      = "\+"
t_MINUS     = "-"
t_TIMES     = "\*"
t_DIVIDE    = "/"
t_INFIX_POW = "\^"


# Prefix operators
BINOPS  = {"pow", "sub2", "sub2_I"}
t_BINOP = "({})".format(")|(".join(BINOPS))

UNOPS = {"abs", "acos", "acosh", "arccos", "arccosh", "arcosh", "arcsin",
         "arcsinh", "arctan", "arctanh", "argcosh", "argsinh", "argtanh",
         "arsinh", "artanh", "asin", "asinh", "atan", "atanh", "cos", "cosh",
         "exp", "log", "sin", "sinh", "sqrt", "tan", "tanh", "floor_power2",
         "sym_interval"}
t_UNOP = "({})".format(")|(".join(UNOPS))


# Variables
def t_NAME(t):
    "([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*"
    if t.value in BINOPS:
        t.type = "BINOP"
    elif t.value in UNOPS:
        t.type = "UNOP"
    elif t.value in {"interval"}:
        t.type = "INTERVAL"
    elif t.value in SYMBOLIC_CONSTS:
        t.type = "SYMBOLIC_CONST"
    else:
        t.type = "NAME"

    return t


# Assignment
t_EQUALS = "="


# Literals
t_FLOAT   = ("("                 # match all floats
             "("                 #  match float with '.'
             "("                 #   match a number base
             "(\d+\.\d+)"        #    <num.num>
             "|"                 #    or
             "(\d+\.)"           #    <num.>
             "|"                 #    or
             "(\.\d+)"           #    <.num>
             ")"                 #
             "("                 #   then match an exponent
             "(e|E)(\+|-)?\d+"   #    <exponent>
             ")?"                #    optionally
             ")"                 #
             "|"                 #  or
             "("                 #  match float without '.'
             "\d+"               #   <num>
             "((e|E)(\+|-)?\d+)" #   <exponent>
             ")"                 #
             ")")
t_INTEGER  = "\d+"
t_INTERVAL = "interval"


# These are the tightest possible enclosures for these transcendental constants.
# GAOL round-trips on the full decimal expansion in its string constructor,
# therefore these intervals are appropriate to substitute for the symbolic
# constant. All intervals when represented by a GAOL interval have a width of
# one ULP.
SYMBOLIC_CONSTS = {
    "pi"      : (("Float",
                  "3.141592653589793115997963468544185161590576171875"),
                 ("Float",
                  "3.141592653589793560087173318606801331043243408203125")),
    "exp1"    : (("Float",
                  "2.718281828459045090795598298427648842334747314453125"),
                 ("Float",
                  "2.71828182845904553488480814849026501178741455078125")),
    "half_pi" : (("Float",
                  "1.5707963267948965579989817342720925807952880859375"),
                 ("Float",
                  "1.5707963267948967800435866593034006655216217041015625")),
    "two_pi"  : (("Float",
                  "6.28318530717958623199592693708837032318115234375"),
                 ("Float",
                  "6.28318530717958712017434663721360266208648681640625")),
}


# Deliminators
t_LPAREN    = "\("
t_RPAREN    = "\)"
t_LBRACE    = "\["
t_RBRACE    = "\]"
t_COMMA     = ","
t_SEMICOLON = ";"


# Non-emitting
t_ignore = (" \t\n\r")
def t_comment(t):
    "\#[^\n]*"
    pass


# Error
def t_error(t):
    print("Illegal character '{}'".format(t), file=sys.stderr)
    sys.exit(-1)








try:
    from gelpia import bin_dir
    _function_lexer = lex.lex(debug=False, optimize=True, outputdir=bin_dir,
                              lextab="main_lextab.py")
except:
    _function_lexer = lex.lex(outputdir="__pycache__")


if __name__ == "__main__":
    try:
        from pass_utils import *
        data = get_runmain_input()
        _function_lexer.input(data)
        while True:
            tok = _function_lexer.token()
            if not tok:
                break
            print(tok)
    except KeyboardInterrupt:
        print("\nGoodbye")
