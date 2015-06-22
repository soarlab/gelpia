import ply.lex
import ply.yacc
'''This simple parser serves to enclose the input interval bounds in strings'''


tokens = (
    "LCURLY",
    "RCURLY",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "COLON",
    "QUOTE",
    "VAR",
    "NUM",
)

t_LCURLY = (r'\{')
t_RCURLY = (r'\}')
t_LPAREN = (r'\(')
t_RPAREN = (r'\)')
t_COMMA  = (r",")
t_COLON  = (r":")
t_QUOTE  = (r"\'")

t_VAR    = (r'([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*')

rint    = r'([1-9]\d*|0)'
rexp    = r'((e|E)(\+|-)?\d+)'

rfloats = [rint + '\.\d+', '\.\d+', rint]


rfloats = list(map(lambda s: '(' + "-?" + s + rexp + '?)', rfloats))

t_NUM = ('|'.join(rfloats))

t_ignore = (' \n\t\r')

def t_error(t):
    print(t)

lexer = ply.lex.lex()

def p_dict(t):
    '''dict : LCURLY kv_pairs RCURLY
            | LCURLY RCURLY'''
    if len(t) == 3: # Empty dictionary
        t[0] = '{}'
    else:
        t[0] = '{' + ', '.join(t[2]) + '}'

def p_kv_pairs(t):
    '''kv_pairs : kv_pairs COMMA kv_pair
                | kv_pair'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[1] + [t[3]]
    
def p_kv_pair(t):
    '''kv_pair : var_dec COLON pair'''
    t[0] = t[1] + " : " + t[3]

def p_var_dec(t):
    '''var_dec : QUOTE VAR QUOTE'''
    t[0] = '"' + t[2] + '"'

def p_pair(t):
    '''pair : LPAREN NUM COMMA NUM RPAREN'''
    t[0] = '("' + t[2] + '", "' + t[4] + '")'
    
def p_error(t):
    print("Syntax error at '{}'".format(t.value))

parser = ply.yacc.yacc()

def process(d):
    return parser.parse(d)

