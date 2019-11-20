

import sys

try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color

try:
    from sly import Lexer
except ModuleNotFoundError:
    logging.error("SLY must be installed for python3", file=sys.stderr)
    sys.exit(-1)


logger = logging.make_module_logger(color.cyan("function_to_lexed"),
                                    logging.HIGH)




class GelpiaLexer(Lexer):
    tokens = [
        # Variables
        "NAME",

        # Prefix operators
        "BINOP",
        "UNOP",

        # Literals
        "SYMBOLIC_CONST",
        "FLOAT",
        "INTEGER",

        # Infix Operators
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "INFIX_POW",

        # Assignment
        "EQUALS",

        # Deliminators
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "COMMA",
        "SEMICOLON",
    ]

    BINOPS = {r"pow", r"sub2"}
    UNOPS = {r"abs", r"acos", r"acosh", r"asin", r"asinh", r"atan", r"atanh",
             r"cos", r"cosh", r"exp", r"log", r"sin", r"sinh", r"sqrt", r"tan",
             r"tanh", r"floor_power2", r"sym_interval"}
    SYMBOLIC_CONSTS = {r"pi", r"exp1", r"half_pi", r"two_pi"}

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')
    ignore_space = r"\s"
    ignore_comment = r"\#.*"
    ignore_labels = r"({})".format(r")|(".join([r"cost:", r"var:"]))

    # Prefix operators
    BINOP = r"({})".format(r")|(".join(BINOPS))
    UNOP = r"({})".format(r")|(".join(UNOPS))

    # Literals
    SYMBOLIC_CONST = r"({})".format(r")|(".join(SYMBOLIC_CONSTS))
    FLOAT = ("("                 # match all floats
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
    INTEGER = r"\d+"

    # Variables
    NAME = r"([a-zA-Z]|\_)([a-zA-Z]|\_|\d)*"
    def NAME(self, t):
        if t.value in self.BINOPS:
            t.type = BINOP
            return t
        if t.value in self.UNOPS:
            t.type = UNOP
            return t
        # Literals
        if t.value in self.SYMBOLIC_CONSTS:
            t.type = SYMBOLIC_CONST
            return t
        return t

    # Infix Operators
    PLUS      = r"\+"
    MINUS     = r"-"
    TIMES     = r"\*"
    DIVIDE    = r"/"
    INFIX_POW = r"\^"

    # Assignment
    EQUALS = r"="

    # Deliminators
    LPAREN = r"\("
    RPAREN = r"\)"
    LBRACE = r"\["
    RBRACE = r"\]"
    COMMA = r","
    SEMICOLON = r";"

    def error(self, t):
        logging.error("Line {}: Bad character '{}'", self.lineno, t.value[0])
        sys.exit(-1)




def function_to_lexed(function):
    lexer = GelpiaLexer()
    tokens = lexer.tokenize(function)
    for token in tokens:
        #logger("{}", token)
        yield token




def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input

        data = get_runmain_input(argv)

        logger("raw: \n{}\n", data)
        tokens = list(function_to_lexed(data))

        logger("tokens: \n{}\n", "\n".join(tokens))

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
