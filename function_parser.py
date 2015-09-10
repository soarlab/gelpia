#!/usr/bin/env python3

from function_lexer import *
import ply.yacc as YACC
import sys as SYS

# this list is tuples of (name, binding) for all bound
# variables in the function. Order matters.
GLOBAL_NAMES = list()

# this set is simply the names of free variables
GLOBAL_FREE_NAMES_SET = list()
GLOBAL_BOUND_NAMES_SET = list() 

def p_function_assign(t):
    '''function : VARIABLE EQUALS expression SEMICOLON function'''
    # make sure this variable being assigned to has not alreaady been used as
    # free
    if t[1] in GLOBAL_FREE_NAMES_SET:
        print("Error free varaible assigned to: Free var '{}'".format(t[1]),
              file=SYS.stderr)
        SYS.exit(-1)
    # set the global
    GLOBAL_NAMES.append((t[1], t[3]))
    GLOBAL_BOUND_NAMES_SET.append(t[1])
    # Returns ['Assign', Name, Binding, Next]
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
    if t[1] not in GLOBAL_BOUND_NAMES_SET:
        if t[1] not in GLOBAL_FREE_NAMES_SET:
            GLOBAL_FREE_NAMES_SET.append(t[1])
            # Returns ['Input', index]
            t[0] = ['Input', len(GLOBAL_FREE_NAMES_SET)-1]
        else:
            t[0] = ['Input', GLOBAL_FREE_NAMES_SET.index(t[1])]
    else:
        # Returns ['Variable', name]
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
    t[0] = ['Interval', t[3][1], t[5][1]]
    
def p_group_passthrough(t):
    '''group : LPAREN expression RPAREN'''
    t[0] = t[2]
    
def p_func_uni(t):
    '''func : UNIOP LPAREN expression RPAREN'''
    # Returns [operator, value]
    t[0] = [t[1], t[3]]

def p_func_bi(t):
    '''func : BINOP LPAREN expression COMMA expression RPAREN'''
    # Returns [operator, value, value]
    if t[1] == 'pow' and t[5][0] == 'Integer':
        t[0] = ['ipow', t[3], t[5]]
    else:
        t[0] = [t[1], t[3], t[5]]

            
def p_error(t):
    print("Syntax error at '{}'".format(t))
    

    
# Generate the parser
parser = YACC.yacc(debug=0, write_tables=0)

def runmain(parser):
    try:
        filename = SYS.argv[1]
        f = open(filename)
        data = f.read()
        f.close()
    except IndexError:
        SYS.stdout.write('Reading from standard input (type EOF to end):\n')
        data = SYS.stdin.read()

    exp = parser.parse(data)

    print(exp)
    print(GLOBAL_NAMES)
    
if __name__ == "__main__":
    runmain(parser)
