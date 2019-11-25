

import sys

try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.magenta("lexed_to_parsed"),
                                    logging.HIGH)

try:
    from sly import Parser
except ModuleNotFoundError:
    logger.error("SLY must be installed for python3")
    sys.exit(-1)

from function_to_lexed import GelpiaLexer


class GelpiaParser(Parser):
    tokens = GelpiaLexer.tokens

    precedence = (("left", "PLUS", "MINUS"),
                  ("left", "TIMES", "DIVIDE"),
                  ("right", "UMINUS"),
                  ("right", "INFIX_POW"),)

    # function
    @_("variable EQUALS expression SEMICOLON function")
    def function(self, p):
        assert(logger("function: variable EQUALS expression SEMICOLON function"))
        assert(logger("          {} EQUALS {} SEMICOLON {}",
                      p.variable, p.expression, p.function))
        return (("Assign", p.variable, p.expression), p.function)

    @_("symbolic_const EQUALS expression SEMICOLON function")
    def function(self, p):
        logger.warning("Dropping assign to symbolic constant '{}'", p[0][1])
        return p.function

    @_("interval variable SEMICOLON function")
    def function(self, p):
        assert(logger("function: interval variable SEMICOLON function"))
        assert(logger("          {} {} SEMICOLON {}",
                      p.variable, p.interval, p.function))
        return (("Assign", p.variable, p.interval), p.function)

    @_("interval symbolic_const SEMICOLON function")
    def function(self, p):
        logger.warning("Dropping assign to symbolic constant '{}'", p[1][1])
        return p.function

    @_("expression_star")
    def function(self, p):
        assert(logger("function: expression_star"))
        assert(logger("          {}", p.expression_star))
        return ("Return", p.expression_star)

    # expression_star
    @_("expression SEMICOLON expression_star")
    def expression_star(self, p):
        assert(logger("expression_star: expression SEMICOLON expression_star"))
        assert(logger("                 {} SEMICOLON {}",
                      p.expression, p.expression_star))
        return ("+", p.expression, p.expression_star)

    @_("expression SEMICOLON")
    def expression_star(self, p):
        assert(logger("expression_star: expression SEMICOLON"))
        assert(logger("                 {} SEMICOLON", p.expression))
        return p.expression

    @_("expression")
    def expression_star(self, p):
        assert(logger("expression_star: expression"))
        assert(logger("                 {}", p.expression))
        return p.expression

    # expression
    @_("expression PLUS expression",
       "expression MINUS expression",
       "expression TIMES expression",
       "expression DIVIDE expression")
    def expression(self, p):
        assert(logger("expression: expression {} expression", p._slice[-2].type))
        assert(logger("            {} {} {}",
                      p.expression0, p._slice[-2].type, p.expression1))
        return (p[1], p.expression0, p.expression1)

    @_("expression INFIX_POW expression")
    def expression(self, p):
        assert(logger("expression: expression INFIX_POW expression"))
        assert(logger("            {} INFIX_POW {}",
                      p.expression0, p.expression1))
        return ("pow", p.expression0, p.expression1)

    @_("MINUS expression %prec UMINUS")
    def expression(self, p):
        assert(logger("expression: MINUS expression %prec UMINUS"))
        assert(logger("            MINUS {}", p.expression))
        return ("neg", p.expression)

    @_("base")
    def expression(self, p):
        assert(logger("expression: base"))
        assert(logger("            {}", p.base))
        return p.base

    # base
    @_("symbolic_const",
       "variable",
       "interval",
       "const",
       "group",
       "func")
    def base(self, p):
        assert(logger("base: {}", p._slice[-1]))
        assert(logger("      {}", p[0]))
        return p[0]

    # variable
    @_("NAME")
    def variable(self, p):
        assert(logger("variable: NAME"))
        assert(logger("          {}", p[0]))
        return ("Name", p[0])

    # interval
    @_("LBRACE negconst COMMA negconst RBRACE")
    def interval(self, p):
        assert(logger("interval: LBRACE negconst COMMA negconst RBRACE"))
        assert(logger("          LBRACE {} COMMA {} RBRACE",
                      p.negconst0, p.negconst1))
        left = p.negconst0
        right = p.negconst1
        low = float(left[1])
        high = float(right[1])

        if low > high:
            logger.error("Upside down intervals not allowed: [{}, {}]",
                         low, high)
            sys.exit(-1)

        if low == high:
            return ("Float", left[1])
        else:
            return ("InputInterval", ("Float", left[1]), ("Float", right[1]))

    @_("LBRACE negconst RBRACE")
    def interval(self, p):
        assert(logger("interval: LBRACE negconst RBRACE"))
        assert(logger("          LBRACE {} RBRACE", p.negconst))
        return ("Float", p.negconst[1])

    # negconst
    @_("MINUS negconst")
    def negconst(self, p):
        assert(logger("negconst: MINUS negconst"))
        assert(logger("          MINUS {}", p.negconst))
        typ, val = p.negconst[0:2]
        if val[0] == "-":
            return (typ, val[1:])
        else:
            return (typ, "-" + val)

    # const
    @_("const")
    def negconst(self, p):
        assert(logger("negconst: const"))
        assert(logger("          {}", p.const))
        return p.const

    @_("integer",
       "float")
    def const(self, p):
        assert(logger("const: {}", p._slice[-1]))
        assert(logger("       {}", p[0]))
        return p[0]

    # integer
    @_("INTEGER")
    def integer(self, p):
        assert(logger("integer: INTEGER"))
        assert(logger("         {}", p[0]))
        return ("Integer", p[0])

    # float
    @_("FLOAT")
    def float(self, p):
        assert(logger("float: FLOAT"))
        assert(logger("       {}", p[0]))
        return ("Float", p[0])

    # group
    @_("LPAREN expression RPAREN")
    def group(self, p):
        assert(logger("group: LPAREN expression RPAREN"))
        assert(logger("       LPAREN {} RPAREN", p.expression))
        return p.expression

    # func
    @_("BINOP LPAREN expression COMMA expression RPAREN")
    def func(self, p):
        assert(logger("func: BINOP LPAREN expression COMMA expression RPAREN"))
        assert(logger("      BINOP LPAREN {} COMMA {} RPAREN",
                      p.expression0, p.expression1))
        return (p[0], p.expression0, p.expression1)

    @_("UNOP LPAREN expression RPAREN")
    def func(self, p):
        assert(logger("func: BINOP LPAREN expression RPAREN"))
        assert(logger("      BINOP LPAREN {} RPAREN", p.expression))
        return (p[0], p.expression)

    # symbolic_const
    @_("SYMBOLIC_CONST")
    def symbolic_const(self, p):
        assert(logger("symbolic_const: SYMBOLIC_CONST"))
        assert(logger("                {}", p[0]))
        return ("SymbolicConst", p[0])

    # errors
    def error(self, p):
        if p:
            logger.error("Line {}: Syntax error at {}".format(p.lineno, str(p)))
        else:
            logger.error("Unexpected end of function")
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

        logger("raw:\n{}\n", data)
        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)

        logger("expression:\n{}\n", tree)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
