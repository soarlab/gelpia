

import sys

try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color

try:
    from sly import Parser
except ModuleNotFoundError:
    logging.error("SLY must be installed for python3", file=sys.stderr)
    sys.exit(-1)

from function_to_lexed import GelpiaLexer


logger = logging.make_module_logger(color.magenta("lexed_to_parsed"),
                                    logging.HIGH)




class GelpiaParser(Parser):
    tokens = GelpiaLexer.tokens

    precedence = (("left", "PLUS", "MINUS"),
                  ("left", "TIMES", "DIVIDE"),
                  ("right", "UMINUS"),
                  ("right", "INFIX_POW"),)


    @_("variable EQUALS expression SEMICOLON function")
    def function(self, p):
        logger("function : variable EQUALS expression SEMICOLON function")
        logger("           {} EQUALS {} SEMICOLON {}",
               p.variable, p.expression, p.function)
        return (("Assign", p.variable, p.expression), p.function)

    @_("symbolic_const EQUALS expression SEMICOLON function")
    def function(self, p):
        logging.warning("Dropping assign to symbolic constant '{}'", p[0][1])
        return p.function

    @_("interval variable SEMICOLON function")
    def function(self, p):
        logger( "function : interval variable SEMICOLON function")
        logger( "           {} {} SEMICOLON {}",
               p.variable, p.interval, p.function)
        return (("Assign", p.variable, p.interval), p.function)

    @_("interval symbolic_const SEMICOLON function")
    def function(self, p):
        logging.warning("Dropping assign to symbolic constant '{}'", p[1][1])
        return p.function

    @_("expression_star")
    def function(self, p):
        logger( "function : expression_star")
        logger( "           {}", p.expression_star)
        return ("Return", p.expression_star)


    @_("expression SEMICOLON expression_star")
    def expression_star(self, p):
        logger("expression_star : expression SEMICOLON expression_star")
        logger("                  {} SEMICOLON {}",
               p.expression, p.expression_star)
        return ("+", p.expression, p.expression_star)

    @_("expression SEMICOLON")
    def expression_star(self, p):
        logger( "expression_star: expression SEMICOLON")
        logger( "                 {} SEMICOLON", p.expression)
        return p.expression

    @_("expression")
    def expression_star(self, p):
        logger( "expression_star: expression")
        logger( "                 {}", p.expression)
        return p.expression


    @_("expression PLUS expression",
       "expression MINUS expression",
       "expression TIMES expression",
       "expression DIVIDE expression")
    def expression(self, p):
        logger("expression: expression {} expression", p._slice[-2].type)
        logger("            {} {} {}",
               p.expression0, p._slice[-2].type, p.expression1)
        return (p[1], p.expression0, p.expression1)

    @_("expression INFIX_POW expression")
    def expression(self, p):
        logger("expression: expression INFIX_POW expression")
        logger("            {} INFIX_POW {}",
               p.expression0, p.expression1)
        return ("pow", p.expression0, p.expression1)

    @_("MINUS expression %prec UMINUS")
    def expression(self, p):
        logger("expression: MINUS expression %prec UMINUS")
        logger("            MINUS {}", p.expression)
        return ("neg", p.expression)

    @_("base")
    def expression(self, p):
        logger("expression : base")
        logger("             {}", p.base)
        return p.base


    @_("symbolic_const",
       "variable",
       "interval",
       "const",
       "group",
       "func")
    def base(self, p):
        logger("base : {}", p._slice[-1])
        logger("       {}", p[0])
        return p[0]


    @_("NAME")
    def variable(self, p):
        logger("variable : NAME")
        logger("           {}", p[0])
        return ("Name", p[0])


    @_("LBRACE negconst COMMA negconst RBRACE")
    def interval(self, p):
        logger("interval : LBRACE negconst COMMA negconst RBRACE")
        logger("           LBRACE {} COMMA {} RBRACE", p.negconst0, p.negconst1)
        left = p.negconst0
        right = p.negconst1
        low = float(left[1])
        high = float(right[1])
        if low > high:
            logging.error("Upside down intervals not allowed: [{}, {}]",
                          low, high)
            sys.exit(-1)
        if low == right:
            return ("Float", left)
        else:
            return ("InputInterval", left, right)

    @_("LBRACE negconst RBRACE")
    def interval(self, p):
        logger("interval : LBRACE negconst RBRACE")
        logger("           LBRACE {} RBRACE", p.negconst)
        return ("Float", p.negconst)


    @_("MINUS negconst")
    def negconst(self, p):
        logger("negconst : MINUS negconst")
        logger("           MINUS {}", p.negconst)
        typ, val = p.negconst[0:2]
        if val[0] == "-":
            return (typ, val[1:])
        else:
            return (typ, "-"+val)

    @_("const")
    def negconst(self, p):
        logger("negconst : const")
        logger("           {}", p.const)
        return p.const


    @_("integer",
       "float")
    def const(self, p):
        logger("const : {}", p._slice[-1])
        logger("        {}", p[0])
        return p[0]


    @_("INTEGER")
    def integer(self, p):
        logger("integer : INTEGER")
        logger("          {}", p[0])
        return ("Integer", p[0])


    @_("FLOAT")
    def float(self, p):
        logger("float : FLOAT")
        logger("        {}", p[0])
        return ("Float", p[0])


    @_("LPAREN expression RPAREN")
    def group(self, p):
        logger("group : LPAREN expression RPAREN")
        logger("        LPAREN {} RPAREN", p.expression)
        return p.expression


    @_("BINOP LPAREN expression COMMA expression RPAREN")
    def func(self, p):
        logger("func : BINOP LPAREN expression COMMA expression RPAREN")
        logger("       BINOP LPAREN {} COMMA {} RPAREN",
               p.expression0, p.expression1)
        return (p[0], p.expression0, p.expression1)

    @_("UNOP LPAREN expression RPAREN")
    def func(self, p):
        logger("func : BINOP LPAREN expression RPAREN")
        logger("       BINOP LPAREN {} RPAREN", p.expression)
        return (p[0], p.expression)

    @_("SYMBOLIC_CONST")
    def symbolic_const(self, p):
        logger("symbolic_const : SYMBOLIC_CONST")
        logger("                 {}", p[0])
        return ("SymbolicConst", p[0])


    def error(self, p):
        if p:
            logging.error("Line {}: Syntax error at {}".format(p.lineno, str(p)))
        else:
            logging.error("Unexpected end of function")
        sys.exit(-1)




def lexed_to_parsed(tokens):
    parser = GelpiaParser()
    return parser.parse(tokens)




def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input
        from function_to_lexed import function_to_lexed
        data = get_runmain_input(argv)
        tokens = function_to_lexed(data)
        logger("raw: \n{}\n", data)
        tree = lexed_to_parsed(tokens)
        logger("expression:")
        logger("  {}", tree)
        return 0
    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
