import ply.lex
import ply.yacc

# Lexer start
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
# Lexer end

# Parser begin
def p_expression(t):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | term'''
    if len(t) == 4: 
        # Returns [operator, lhs, rhs]
        t[0] = [t[2], t[1], t[3]]
    else: 
        # Passthrough
        t[0] = t[1]


def p_term(t):
    '''term : term TIMES uop
            | term DIV uop
            | uop'''
    if len(t) == 4:
        # Returns [operator, lhs, rhs]
        t[0] = [t[2], t[1], t[3]]
    else:
        # Passthrough
        t[0] = t[1]

def p_uop(t):    
    '''uop : MINUS base
           | base'''
    if len(t) == 3:
        # Unary negation
        t[0] = ['Neg', t[2]]
    else:
        # Passthrough
        t[0] = t[1]


def p_base(t):
    '''base : name
            | number
            | group
            | func'''
    # Passthrough
    t[0] = t[1]

def p_name(t):
    '''name : VAR'''
    # Variable is ['Name', var_name]
    t[0] = ['Name', t[1]]
    
def p_number(t):
    '''number : NUM'''
    # Number is ['Value', number]
    t[0] = ['Value', t[1]]

def p_group(t):
    '''group : LPAREN expression RPAREN'''
    # Passes through a grouped expression
    t[0] = t[2]

def p_func(t):
    '''func : VAR LPAREN args RPAREN'''
    # Function call is ['Call', function_name, [list_of_args]]
    t[0] = ['Call', t[1]] + [t[3]]


def p_args(t):
  '''args : args COMMA expression
          | expression'''
  if t[1][0] == 'Args':
    # Args is a list of expressions with the first argument as 'Args'
    t[0] = t[1] + [t[3]]
  else:
    # An expression being passed through as an argument
    t[0] = ['Args', t[1]]

def p_error(t):
    print("Syntax error at '{}'".format(t.value))

# Generate the parser
parser = ply.yacc.yacc()

# Parser end

def collect_vars(exp):
    '''Examines expression recursively to return a set of all variables found
       inside. Additionally prepends a '_' to protect user variables from 
       automatically generated variables.'''
    result = set()
    if len(exp) == 2:
        if exp[0] == 'Name':
          exp[1] = '_' + exp[1] # Prepend an '_'
          result.add(exp[1])
        if exp[0] == 'Neg': # Examine the negated expression
            result = result | collect_vars(exp[1])
    if len(exp) == 3:
        if exp[0] == 'Call':
          for v in exp[2][1:]: # Examine the arguments list
            result = result | collect_vars(v)
        else: # Otherwise the expression is a binary operation and we need
              # to collect both sides.
            result = result | collect_vars(exp[1]) | collect_vars(exp[2])
    return result

def lift_constants(exp, i_list, constants):
  ''' Examines the expression to extract the constants found within. Currently
      a constant is a Value or a function call to interval. These are mapped to
      a renamed internal variable.
      i_list holds an integer to create a unique variable substitution.
      constants is a dictionary mapping intervals to the replacement variable
      name.'''
  if exp[0] == 'Value': # Replace a value constant
    if not (exp[1], exp[1]) in constants.keys():
      constants[(exp[1], exp[1])] = 'c' + str(i_list[0])
      i_list[0] += 1
    
    replacement = constants[(exp[1], exp[1])]
    exp[:] = ['InternalName', replacement]
  elif exp[0] == 'Call' and exp[1] == 'interval': # Replace an interval constant
    args = exp[2]
    if not (args[1][1], args[2][1]) in constants.keys():
      constants[(args[1][1], args[2][1])] = 'c' + str(i_list[0])
      i_list[0] += 1

    replacement = constants[(args[1][1], args[2][1])]
    exp[:] = ['InternalName', replacement]
  else: # Otherwise dig deeper into the expression to find constants
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
  '''Returns a dictionary of constants found in expression which maps intervals
     to the replacement variable name.'''
  constants = dict()
  i_list = [0]
  lift_constants(exp, i_list, constants)
  return constants
 
def decl_constants(constants, const_trans):
  result = "// Constants from expression\n"
  for interval in constants.keys():
    name = constants[interval]
    result += const_trans(name, interval[0], interval[1])
  return result
      
def decl_vars(variables, var_transform):
    '''Returns a string of the c++ declarations of variables'''
    result = '// Variables from expression\n'
    for v in variables.keys():
        result += var_transform(v, variables[v]) + '\n'

    return result + '\n'

def expressify(exp, val_trans, func_trans):
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
          
def mpfi_process(exp, val_trans, func_trans):
    return 'return interval(' + expressify(exp, val_trans, func_trans) + ');\n'

def filib_process(exp, val_trans, func_trans):
    return 'return fast_interval(' + expressify(exp, val_trans, func_trans) + ');\n'


def deriv_exp(exp, var):
  if exp[0] == '+':
    return ['+', deriv_exp(exp[1], var), deriv_exp(exp[2], var)]
  if exp[0] == '-':
    return ['-', deriv_exp(exp[1], var), deriv_exp(exp[2], var)]
  if exp[0] == 'Neg':
    return ['Neg', deriv_exp(exp[1], var)]
  if exp[0] == '*':
    f = exp[1]
    g = exp[2]
    df = deriv_exp(f, var)
    dg = deriv_exp(g, var)
    return ['+',
            ['*', f, dg],
            ['*', df, g]]
  if exp[0] == '/':
    f = exp[1]
    g = exp[2]
    df = deriv_exp(f, var)
    dg = deriv_exp(g, var)
    return ['/', 
            ['-', 
             ['*', df, g],
             ['*', f, dg]],
            ['Call', 'pow', ['Args', g, ['Value', '2']]]]

  if exp[0] == 'Call':
    if exp[1] == 'pow':
      return ['*',
              ['*',
               exp[2][2],
               ['Call', 'pow', ['Args', exp[2][1], ['Value', str(int(exp[2][2][1]) - 1)]]]],
              deriv_exp(exp[2][1], var)]
    if exp[1] == 'sin':
      return ['*',
              ['Call', 'cos', ['Args', exp[2][1]]],
              deriv_exp(exp[2][1], var)]
    if exp[1] == 'cos':
      return ['*',
              ['Neg',
              ['Call', 'sin', ['Args', exp[2][1]]]],
              deriv_exp(exp[2][1], var)]
  if exp[0] == 'InternalName' or exp[0] == 'Value':
    return ['Value', '0']
  if exp[0] == 'Name':
    if exp[1] == '_' + var:
      return ['Value', '1']
    else:
      return ['Value', '0']
  print('missed', exp)
  return exp

def simplify(exp):
  result = exp, False
  if exp[0] == '+' and exp[1][0] == 'Value' and exp[1][1] == '0':
    result = exp[2], True
  elif exp[0] == '+' and exp[2][0] == 'Value' and exp[2][1] == '0':
    result = exp[1], True

  elif (exp[0] == '*' and 
      exp[1][0] == 'Value' and 
      exp[1][1] == '1'):
    result =  exp[2], True
  elif (exp[0] == '*' and 
      exp[2][0] == 'Value' and 
      exp[2][1] == '1'):
    result = exp[1], True
  elif exp[0] == '*' and exp[1][0] == 'Value' and exp[1][1] == '0':
    result =  ['Value', '0'], True
  elif exp[0] == '*' and exp[2][0] == 'Value' and exp[2][1] == '0':
    result = ['Value', '0'], True

  elif exp[0] == '-' and exp[2][0] == 'Value' and exp[2][1] == '0':
    result = exp[1], True
  elif exp[0] == '-' and exp[1][0] == 'Value' and exp[1][1] == '0':
    result = ['Neg', exp[2]], True

  elif exp[0] == '/' and exp[2][0] == 'Value' and exp[2][1] == '1':
    result = exp[1], True
  elif exp[0] == '/' and exp[1][0] == 'Value' and exp[1][1] == '0':
    result = ['Value', '0'], True

  elif exp[0] in ('+', '*', '-', '/'):
    left, lchange = simplify(exp[1])
    right, rchange = simplify(exp[2])
    result = [exp[0], left, right], lchange or rchange

  elif exp[0] == 'Call':
    arg_simp, ch = simplify(exp[2][1])
    new_exp = ['Call', exp[1], ['Args', arg_simp] + exp[2][2:]]
    result = new_exp, ch

  return result
    
def simplify_wrap(exp):
  changed = True
  result = exp
  while changed:
    result, changed = simplify(result)
  return result

def get_body(s, variables, val_trans, var_trans, const_trans, func_trans, lift_constants, process):
    exp = parser.parse(s)
    import rewriter.post_order
    print(rewriter.post_order.postorder(exp))
    if lift_constants:
      constants = lift_constants_wrap(exp)
    else:
      constants = dict()
      
    v = collect_vars(exp)
    for v in variables.keys():
      print(v + ':')
      df = deriv_exp(exp, v)
      from pprint import pprint
      pprint(simplify_wrap(df))

    return (decl_vars(variables, var_trans) + 
            decl_constants(constants, const_trans) + 
            process(exp, val_trans, func_trans))
 
def mpfi_get_body(s, variables, lift_constants = True):
 return get_body(s, variables, mpfi_val_trans, mpfi_var_trans, 
                  mpfi_const_trans, mpfi_func_trans, lift_constants, mpfi_process)

def mpfi_func_trans(expression, val_trans, func_trans):
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

def mpfi_val_trans(value):
  return 'interval({}).get_value()'.format(value)
  
def mpfi_const_trans(name, inf, sup):
  return '''static const large_float_t {0}_l("{1}");
static const large_float_t {0}_u("{2}");
static const interval_t {0}({0}_l, {0}_u);\n\n'''.format(name, inf, sup)

def mpfi_var_trans(name, value):
  return 'const interval_t & _' + name + ' =  X[' + str(value) + '];'

def filib_get_body(s, variables, lift_constants = True):
  return get_body(s, variables, filib_val_trans, filib_var_trans, 
                  filib_const_trans, filib_func_trans, lift_constants, filib_process)

def filib_func_trans(expression, val_trans, func_trans):
  if expression[1] == 'interval':
    args = expression[2]
    assert(len(args) == 3) # ['Call', 'interval', ['Args', NUM, NUM]]
    assert(args[1][0] == 'Value')
    assert(args[2][0] == 'Value')
    return '(fast_interval(' + args[1][1] + ', ' + args[2][1] + ').get_value())'
  elif expression[1] == 'pow':
    args = expression[2]
    assert(len(args) == 3) #['Args', var, power_int]
    return '(pow(' + expressify(args[1], val_trans, func_trans) + ", " + args[2][1] + '))'
  else:
    return ('(' + expression[1] + 
            "(" + expressify(expression[2][1], val_trans, func_trans) + ')' + ')')

def filib_val_trans(value):
  return 'fast_interval({}).get_value()'.format(value)

def filib_const_trans(name, inf, sup):
  return '''static const fast_interval_t {0}({1}, {2});\n\n'''.format(name, inf, sup)

def filib_var_trans(name, value):
  return 'const fast_interval_t & _' + name + ' =  X[' + str(value) + '];'

