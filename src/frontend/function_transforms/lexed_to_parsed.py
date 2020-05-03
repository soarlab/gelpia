

from function_to_lexed import GelpiaLexer
import gelpia_logging as logging
import color_printing as color

import sys

logger = logging.make_module_logger(color.magenta("lexed_to_parsed"),
                                    logging.HIGH)

try:
    from sly import Parser
except ModuleNotFoundError:
    logger.error("SLY must be installed for python3")
    sys.exit(1)


class GelpiaParser(Parser):
    tokens = GelpiaLexer.tokens

    precedence = (("left", "PLUS", "MINUS"),
                  ("left", "TIMES", "DIVIDE"),
                  ("right", "UMINUS"),
                  ("right", "INFIX_POW"),)

    # function
    @_("assignment SEMICOLON function")
    def function(self, p):
        return (p.assignment, *p.function)

    @_("constraint SEMICOLON function")
    def function(self, p):
        return (p.constraint, *p.function)

    @_("cost SEMICOLON function")
    def function(self, p):
        return (p.cost, *p.function)

    @_("assignment SEMICOLON",
       "assignment")
    def function(self, p):
        return (p.assignment,)

    @_("constraint SEMICOLON",
       "constraint")
    def function(self, p):
        return (p.constraint,)

    @_("cost SEMICOLON",
       "cost")
    def function(self, p):
        return (p.cost,)

    # assignment
    @_("variable EQUALS expression")
    def assignment(self, p):
        return ("Assign", p.variable, p.expression)

    @_("interval variable")
    def assignment(self, p):
        return ("Assign", p.variable, p.interval)

    @_("symbolic_const EQUALS expression")
    def assignment(self, p):
        return ("Assign", p.symbolic_const, p.expression)

    @_("interval symbolic_const")
    def assignment(self, p):
        return ("Assign", p.symbolic_const, p.interval)

    # constraint
    @_("expression comparison expression")
    def constraint(self, p):
        return ("Constrain", p.comparison, p.expression0, p.expression1)

    # cost
    @_("expression")
    def cost(self, p):
        return ("Cost", p.expression)

    # comparison
    @_("LESS_THAN",
       "GREATER_THAN",
       "LESS_THAN_OR_EQUAL",
       "GREATER_THAN_OR_EQUAL",
       "EQUALS")
    def comparison(self, p):
        return p[0]

    # expression
    @_("expression PLUS expression",
       "expression MINUS expression",
       "expression TIMES expression",
       "expression DIVIDE expression")
    def expression(self, p):
        return (p[1], p.expression0, p.expression1)

    @_("expression INFIX_POW expression")
    def expression(self, p):
        return ("pow", p.expression0, p.expression1)

    @_("MINUS expression %prec UMINUS")
    def expression(self, p):
        return ("neg", p.expression)

    @_("base")
    def expression(self, p):
        return p.base

    # base
    @_("symbolic_const",
       "variable",
       "interval",
       "const",
       "group",
       "func")
    def base(self, p):
        return p[0]

    # variable
    @_("NAME")
    def variable(self, p):
        return ("Name", p[0])

    # interval
    @_("LBRACE negconst COMMA negconst RBRACE")
    def interval(self, p):
        left = p.negconst0
        right = p.negconst1
        low = float(left[1])
        high = float(right[1])

        if low > high:
            logger.error("Upside down intervals not allowed: [{}, {}]",
                         low, high)
            sys.exit(1)

        if low == high:
            return ("Float", left[1])
        else:
            return ("InputInterval", ("Float", left[1]), ("Float", right[1]))

    @_("LBRACE negconst RBRACE")
    def interval(self, p):
        return ("Float", p.negconst[1])

    # negconst
    @_("MINUS negconst")
    def negconst(self, p):
        typ, val = p.negconst[0:2]
        if val[0] == "-":
            return (typ, val[1:])
        else:
            return (typ, "-" + val)

    # const
    @_("const")
    def negconst(self, p):
        return p.const

    @_("integer",
       "float")
    def const(self, p):
        return p[0]

    # integer
    @_("INTEGER")
    def integer(self, p):
        return ("Integer", p[0])

    # float
    @_("FLOAT")
    def float(self, p):
        return ("Float", p[0])

    # group
    @_("LPAREN expression RPAREN")
    def group(self, p):
        return p.expression

    # func
    @_("BINOP LPAREN expression COMMA expression RPAREN")
    def func(self, p):
        return (p[0], p.expression0, p.expression1)

    @_("UNOP LPAREN expression RPAREN")
    def func(self, p):
        return (p[0], p.expression)

    # symbolic_const
    @_("SYMBOLIC_CONST")
    def symbolic_const(self, p):
        return ("SymbolicConst", p[0])

    # errors
    def error(self, p):
        if p:
            logger.error("Line {}: Syntax error at {}".format(p.lineno, str(p)))
        else:
            logger.error("Unexpected end of function")
        sys.exit(1)


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
