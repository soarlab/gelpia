import ply.lex
import ply.yacc

tokens = (
    "VAR",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIV",
    "NUM",
    "LPAREN",
    "RPAREN",
    "COMMA",
)

t_VAR   = (r'([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*')
t_PLUS  = (r'\+')
t_MINUS = (r'-')
t_TIMES = (r'\*')
t_DIV   = (r'/')
t_COMMA = (r",")


rint    = r'([1-9]\d*|0)'
rexp    = r'((e|E)(\+|-)?\d+)'

rfloats = [rint + '\.\d+', '\.\d+', rint]


rfloats = list(map(lambda s: '(' + s + rexp + '?)', rfloats))

t_NUM = ('|'.join(rfloats))
         
t_LPAREN = (r'\(')

t_RPAREN = (r'\)')

t_ignore = (' \n\t\r')

def t_error(t):
  print(t);

lexer = ply.lex.lex()

def p_expression(t):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | term'''
    if len(t) == 4:
        t[0] = [t[2], t[1], t[3]]
    else:
        t[0] = t[1]


def p_term(t):
    '''term : term TIMES uop
            | term DIV uop
            | uop'''
    if len(t) == 4:
        t[0] = [t[2], t[1], t[3]]
    else:
        t[0] = t[1]

def p_uop(t):
    '''uop : MINUS base
           | base'''
    if len(t) == 3:
        t[0] = ['Neg', t[2]]
    else:
        t[0] = t[1]


def p_base(t):
    '''base : name
            | number
            | group
            | func'''
    t[0] = t[1]

def p_name(t):
    '''name : VAR'''
    t[0] = ['Name', t[1]]
    
def p_number(t):
    '''number : NUM'''
    t[0] = ['Value', t[1]]

def p_group(t):
    '''group : LPAREN expression RPAREN'''
    t[0] = t[2]

def p_func(t):
    '''func : VAR LPAREN args RPAREN'''
    t[0] = ['Call', t[1]] + [t[3]]


def p_args(t):
  '''args : args COMMA expression
          | expression'''
  if t[1][0] == 'Args':
    t[0] = t[1] + [t[3]]
  else:
    t[0] = ['Args', t[1]]

def p_error(t):
    print("Syntax error at '{}'".format(t.value))

# Generate the parser
parser = ply.yacc.yacc()

tmp_count = 0;

def tmp_name():
    global tmp_count
    tmp_count += 1
    return ('Name', '_tmp_{}'.format(str(tmp_count)))

def collect_nums(exp):
    nums = set()
    if not isinstance(exp, list):
        return nums
    elif exp[0] == 'Value':
        new_name = tmp_name();
        nums.add((new_name, exp[1]))
        exp[0] = new_name[0]
        exp[1] = new_name[1]

    for sl in exp:
        nums = nums | collect_nums(sl)
    return nums

def process_ops(exp, func_transform = lambda x: x):
    result = ''
    new_exp = exp
    if len(exp) == 1: #
        pass
    elif len(exp) == 3:
        if exp[0] != 'Call':
            left, new_left = process_ops(exp[1])
            exp[1] = new_left
            right, new_right = process_ops(exp[2])
            exp[2] = new_right
            new_exp = tmp_name()
            result = left + right + 'const mpz_class ' + new_exp[1] + '(' + str(exp[1][1]) + str(exp[0]) + str(exp[2][1]) + ');\n'
        else:
            inner, new_inner = process_ops(exp[2])
            exp[2] = new_inner
            new_exp = tmp_name()
            result = inner + 'type ' + new_exp[1] + ' = ' + func_transform(exp[1]) + '(' + str(exp[2][1]) + ');\n'
    return result, new_exp;
    
#def process(exp):
#    nums = collect_nums(exp)
#    result = ''
#    for x in nums:
#        result += 'const mpz_class ' + x[0][1] + '("'+x[1] + '");\n'

#    op_list, exp_result = process_ops(exp)
#    result += op_list
#    result += 'return ' + exp_result[1] + ';\n';
#    return result

def collect_vars(exp):
    result = set()
    if len(exp) == 2:
        if exp[0] == 'Name':
          exp[1] = '_' + exp[1]
          result.add(exp[1])
        if exp[0] == 'Neg':
            result = result | collect_vars(exp[1])
    if len(exp) == 3:
        if exp[0] == 'Call':
          for v in exp[2][1:]:
            result = result | collect_vars(v)
        else:
            result = result | collect_vars(exp[1]) | collect_vars(exp[2])
    return result

def lift_constants(exp, i_list, constants):
  if exp[0] == 'Value':
    if not (exp[1], exp[1]) in constants.keys():
      constants[(exp[1], exp[1])] = 'c' + str(i_list[0])
      i_list[0] += 1
    
    replacement = constants[(exp[1], exp[1])]
    exp[:] = ['InternalName', replacement]
  elif exp[0] == 'Call' and exp[1] == 'interval':
    args = exp[2]
    if not (args[1][1], args[2][1]) in constants.keys():
      constants[(args[1][1], args[2][1])] = 'c' + str(i_list[0])
      i_list[0] += 1

    replacement = constants[(args[1][1], args[2][1])]
    exp[:] = ['InternalName', replacement]
  else:
    if len(exp) == 2:
      if exp[0] == 'Neg':
        lift_constants(exp[1], i_list, constants)
    else:
      if exp[0] == 'Call':
        lift_constants(exp[2][1], i_list, constants)
      else:
        lift_constants(exp[1], i_list, constants)
        lift_constants(exp[2], i_list, constants)

def lift_constants_wrap(exp):
  constants = dict()
  i_list = [0]
  lift_constants(exp, i_list, constants)
  return constants
        
      
def decl_vars(variables):
    i = 0
    result = '// Variables from expression\n'
    for v in variables.keys():
        result += 'const interval_t & _' + v + ' =  X[' + str(variables[v]) + '];\n'
        i += 1
    return result + '\n'

def expressify(exp, val_trans = lambda x: 'interval("' + x + '", "' + x + '").get_value()',
               func_trans = lambda x: x):
    if len(exp) == 2:
        if exp[0] == 'Name':
            return exp[1]
        if exp[0] == 'InternalName':
            return exp[1]
        if exp[0] == 'Value':
            return '(' + val_trans(exp[1]) + ')'
        if exp[0] == 'Neg':
            return '(-' + expressify(exp[1], val_trans, func_trans) + ')'
    if len(exp) == 3:
        if exp[0] == 'Call':
             return func_trans(exp, val_trans, func_trans);
        else: # Binary operations
            return '(' + expressify(exp[1], val_trans, func_trans) + exp[0] + expressify(exp[2], val_trans, func_trans) + ')'
          
def process(exp):
    return 'return interval(' + expressify(exp, func_trans = gelpia_functions) + ');\n'

def decl_constants(constants):
  result = "// Constants from expression\n"
  for interval in constants.keys():
    name = constants[interval]
    result += '''static const large_float_t {0}_l("{1}");
static const large_float_t {0}_u("{2}");
static const interval_t {0}({0}_l, {0}_u);\n\n'''.format(name, interval[0], interval[1])
                                           
  return result
                                                                         

def get_body(s, variables):
    exp = parser.parse(s)
    constants = lift_constants_wrap(exp)
    v = collect_vars(exp)
    return (decl_vars(variables) + decl_constants(constants) + process(exp))

def gelpia_functions(expression, val_trans, func_trans):
  if expression[1] == 'interval':
    args = expression[2]
    assert(len(args) == 3) # ['Call', 'interval', ['Args', NUM, NUM]]
    assert(args[1][0] == 'Value')
    assert(args[2][0] == 'Value')
    return '(interval("' + args[1][1] + '", "' + args[2][1] + '").get_value())'
  elif expression[1] == 'pow':
    args = expression[2]
    assert(len(args) == 3) #['Args', var, power_int]
    return '(pow(' + expressify(args[1], val_trans, func_trans) + ", " + args[2][1] + '))'
  else:
    return ('(' + expression[1] + 
            "(" + expressify(expression[2][1], val_trans, func_trans) + ')' + ')')
  
