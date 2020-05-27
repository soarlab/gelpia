

import sys

import function_to_lexed


BINOPS = function_to_lexed.GelpiaLexer.BINOPS
UNOPS = function_to_lexed.GelpiaLexer.UNOPS
SYMBOLIC_CONSTS = function_to_lexed.GelpiaLexer.SYMBOLIC_CONSTS

BINOPS.update({"+", "-", "*", "/", "powi"})
UNOPS.update({"dabs", "datanh", "neg"})
ATOMS = {"ConstantInterval", "Float", "InputInterval", "Integer",
         "SymbolicConst"}
INFIX = {"+", "-", "*", "/"}
ASSOC = {"+", "*"}


def get_runmain_input(argv):
    """
    Reads from a file specified on the command line, or stdin if no file
    """
    try:
        filename = argv[1]
        with open(filename, "r") as f:
            data = f.read()
    except IndexError:
        sys.stdout.write("Reading from standard input (type EOF to end):\n")
        data = sys.stdin.read()

    return data


def extract_exp_from_diff(diff_exp):
    """
    Takes in an expression that has been ran through pass_reverse_diff and
    returns just the main expression, not the derrivatives
    """
    if diff_exp[0] != "Tuple":
        return diff_exp
    exp = diff_exp[1]
    return exp
