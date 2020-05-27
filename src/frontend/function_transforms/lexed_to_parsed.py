

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

    precedence = (("left", "OR", "AND"),
                  ("left", "PLUS", "MINUS"),
                  ("left", "TIMES", "DIVIDE"),
                  ("right", "UMINUS"),
                  ("right", "INFIX_POW"),)

    # function
    @_("assignment SEMICOLON function")
    def function(self, p):
        logger("function: assignment SEMICOLON function")
        logger("          {}; {}", p.assignment, *p.function)
        return (p.assignment, *p.function)

    @_("compound_constraint SEMICOLON function")
    def function(self, p):
        logger("function: compound_constraint SEMICOLON function")
        logger("          {}; {}", p.compound_constraint, *p.function)
        return (p.compound_constraint, *p.function)

    @_("cost SEMICOLON function")
    def function(self, p):
        logger("function: cost SEMICOLON function")
        logger("          {}; {}", p.cost, *p.function)
        return (p.cost, *p.function)

    @_("assignment SEMICOLON",
       "assignment")
    def function(self, p):
        logger("function: assignment SEMICOLON?")
        logger("          {}", p.asignment)
        return (p.assignment,)

    @_("compound_constraint SEMICOLON",
       "compound_constraint")
    def function(self, p):
        logger("function: compound_constraint SEMICOLON?")
        logger("          {}", p.compound_constraint)
        return (p.compound_constraint,)

    @_("cost SEMICOLON",
       "cost")
    def function(self, p):
        logger("function: cost SEMICOLON?")
        logger("          {}", p.cost)
        return (p.cost,)

    # assignment
    @_("variable EQUALS expression")
    def assignment(self, p):
        logger("assignment: variable EQUALS expression")
        logger("            {} = {}", p.variable, p.expression)
        return ("Assign", p.variable, p.expression)

    @_("interval variable")
    def assignment(self, p):
        logger("assignment: interval variable")
        logger("            {} {}", p.variable, p.interval)
        return ("Assign", p.variable, p.interval)

    @_("symbolic_const EQUALS expression")
    def assignment(self, p):
        logger("assignment: symbolic_const EQUALS expression")
        logger("            {} = {}", p.symbolic_const, p.expression)
        return ("Assign", p.symbolic_const, p.expression)

    @_("interval symbolic_const")
    def assignment(self, p):
        logger("assignment: interval symbolic_const")
        logger("            {} {}", p.symbolic_const, p.interval)
        return ("Assign", p.symbolic_const, p.interval)

    # compound constraint
    @_("compound_constraint OR compound_constraint",
       "compound_constraint AND compound_constraint")
    def compound_constraint(self, p):
        logger("compound_constraint: compound_constraint boolean_op compound_constraint")
        logger("                     {} {} {}", p.compound_constraint0, p[1], p.compound_constraint1)
        comp = "and" if p[1] == "&&" else "or"
        return (comp, p.compound_constraint0, p.compound_constraint1)

    @_("NOT LPAREN compound_constraint RPAREN")
    def compound_constraint(self, p):
        logger("compound_constraint: NOT LPAREN compound_constraint RPAREN")
        logger("                     ~( {} )", p.compound_constraint)
        return ("not", p.compound_constraint)

    @_("LPAREN compound_constraint RPAREN")
    def compound_constraint(self, p):
        logger("compound_constraint: LPAREN compound_constraint RPAREN")
        logger("                     ( {} )", p.compound_constraint)
        return p.compound_constraint

    @_("constraint")
    def compound_constraint(self, p):
        logger("compound_constraint: constraint")
        logger("                     {}", p.constraint)
        return p.constraint

    # constraint
    @_("expression comparison expression")
    def constraint(self, p):
        logger("constraint: expression comparison expression")
        logger("            {} {} {}", p.expression0, p.comparison, p.expression1)
        return ("Constrain", p.comparison, p.expression0, p.expression1)

    # cost
    @_("expression")
    def cost(self, p):
        logger("cost: expression")
        logger("      {}", p.expression)
        return ("Cost", p.expression)

    # comparison
    @_("LESS_THAN",
       "GREATER_THAN",
       "LESS_THAN_OR_EQUAL",
       "GREATER_THAN_OR_EQUAL")
    def comparison(self, p):
        logger("comparison: <comparison>")
        logger("            {}", p[0])
        return p[0]

    # expression
    @_("expression PLUS expression",
       "expression MINUS expression",
       "expression TIMES expression",
       "expression DIVIDE expression")
    def expression(self, p):
        logger("expression: expression <op> expression")
        logger("            {} {} {}", p.expression0, p[1], p.expression1)
        return (p[1], p.expression0, p.expression1)

    @_("expression INFIX_POW expression")
    def expression(self, p):
        logger("expression: expression INFIX_POW expression")
        logger("            {} ^ {}", p.expression0, p.expression1)
        return ("pow", p.expression0, p.expression1)

    @_("MINUS expression %prec UMINUS")
    def expression(self, p):
        logger("expression: MINUS expression %prec UMINUS")
        logger("            - {}", p.expression)
        return ("neg", p.expression)

    @_("base")
    def expression(self, p):
        logger("expression: base")
        logger("            {}", p.base)
        return p.base

    # base
    @_("symbolic_const",
       "variable",
       "interval",
       "const",
       "group",
       "func")
    def base(self, p):
        logger("base: <base>")
        logger("      {}", p[0])
        return p[0]

    # variable
    @_("NAME")
    def variable(self, p):
        logger("variable: NAME")
        logger("          {}", p[0])
        return ("Name", p[0])

    # interval
    @_("LBRACE negconst COMMA negconst RBRACE")
    def interval(self, p):
        logger("interval: LBRACE negconst COMMA negconst RBRACE")
        logger("          [ {} , {} ]", p.negconst0, p.negconst1)
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
        logger("interval: LBRACE negconst RBRACE")
        logger("          [ {} ]", p.negconst[1])
        return ("Float", p.negconst[1])

    # negconst
    @_("MINUS negconst")
    def negconst(self, p):
        logger("negconst: MINUS negconst")
        logger("          - {}", p.negconst)
        typ, val = p.negconst[0:2]
        if val[0] == "-":
            return (typ, val[1:])
        else:
            return (typ, "-" + val)

    # const
    @_("const")
    def negconst(self, p):
        logger("negconst: const")
        logger("          {}", p.const)
        return p.const

    @_("integer",
       "float")
    def const(self, p):
        logger("const: <const>")
        logger("       {}", p[0])
        return p[0]

    # integer
    @_("INTEGER")
    def integer(self, p):
        logger("integer: INTEGER")
        logger("         {}", p[0])
        return ("Integer", p[0])

    # float
    @_("FLOAT")
    def float(self, p):
        logger("float: FLOAT")
        logger("       {}", p[0])
        return ("Float", p[0])

    # group
    @_("LPAREN expression RPAREN")
    def group(self, p):
        logger("group: LPAREN expression RPAREN")
        logger("       ( {} )", p.expression)
        return p.expression

    # func
    @_("BINOP LPAREN expression COMMA expression RPAREN")
    def func(self, p):
        logger("func: BINOP LPAREN expression COMMA expression RPAREN")
        logger("      {} ( {} , {} )", p[0], p.expression0, p.expression1)
        return (p[0], p.expression0, p.expression1)

    @_("UNOP LPAREN expression RPAREN")
    def func(self, p):
        logger("func: UNOP LPAREN expression RPAREN")
        logger("      {} ( {} )", p[0], p.expression)
        return (p[0], p.expression)

    # symbolic_const
    @_("SYMBOLIC_CONST")
    def symbolic_const(self, p):
        logger("symbolic_const: SYMBOLIC_CONST")
        logger("                {}", p[0])
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
