

import re
import sys
import fractions

from expression_walker import walk
from pass_utils import INFIX, BINOPS, UNOPS, SYMBOLIC_CONSTS
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.blue("output_smt2"),
                                    logging.HIGH)


def output_smt2(constraints):

    def _e_bool_op(work_stack, count, exp):
        assert(exp[0] in {"or", "and"})
        assert(len(exp) == 3)
        work_stack.append((True, count, exp[0]))
        work_stack.append((False, 2, exp[2]))
        work_stack.append((False, 2, exp[1]))

    def _e_bool_neg(work_stack, count, exp):
        assert(exp[0] == "not")
        assert(len(exp) == 2)
        work_stack.append((True, count, exp[0]))
        work_stack.append((False, 1, exp[1]))

    def _e_constrain(work_stack, count, exp):
        assert(exp[0] == "Constrain")
        assert(len(exp) == 4)
        work_stack.append((True, count, exp[0]))
        work_stack.append((False, 3, exp[3]))
        work_stack.append((False, 3, exp[2]))
        work_stack.append((True,  3, exp[1]))

    def _e_float(work_stack, count, exp):
        assert(exp[0] == "Float")
        assert(len(exp) == 2)
        if "e" not in exp[1] and "E" not in exp[1]:
            work_stack.append((True, count, [exp[1]]))
        else:
            match = re.match(r"([0-9]*\.?[0-9]*)[eE]([-+]?[0-9]*)", exp[1])
            base = match.group(1)
            expo = match.group(2).replace("+", "")
            num = ["(* ", base, " (^ 10.0 ", expo, "))"]
            work_stack.append((True, count, num))

    def _e_sqrt(work_stack, count, exp):
        assert(exp[0] == "sqrt")
        assert(len(exp) == 2)
        work_stack.append((True, count, "pow"))
        work_stack.append((False, 2, ("Float", "0.5")))
        work_stack.append((False, 2, exp[1]))

    def _e_atom(work_stack, count, exp):
        assert(len(exp) == 2)
        work_stack.append((True, count, [exp[1]]))

    my_expand_dict = {"or":            _e_bool_op,
                      "and":           _e_bool_op,
                      "not":           _e_bool_neg,
                      "Constrain":     _e_constrain,
                      "Integer":       _e_atom,
                      "Float":         _e_float,
                      "sqrt":          _e_sqrt,
                      "Input":         _e_atom}

    def _contract_sexp(work_stack, count, args):
        retval = ["(", args[0]]
        for a in args[1:]:
            if type(a) != list:
                logger("Thing: {}", a)
            retval += [" "] + a
        retval += [")"]
        work_stack.append((True, count, retval))

    def _c_constrain(work_stack, count, args):
        retval = ["(", args[1], " "] + args[2] + [" "] + args[3] + [")"]
        work_stack.append((True, count, retval))

    def _c_pow(work_stack, count, args):
        retval = ["(^ "] + args[1] + [" "] + args[2] + [")"]
        work_stack.append((True, count, retval))

    def _c_neg(work_stack, count, args):
        retval = ["(- "] + args[1] + [")"]
        work_stack.append((True, count, retval))

    my_contract_dict = {}
    my_contract_dict.update(zip(BINOPS,
                                [_contract_sexp for _ in BINOPS]))
    my_contract_dict.update(zip(UNOPS,
                                [_contract_sexp for _ in UNOPS]))
    my_contract_dict.update(zip(INFIX,
                                [_contract_sexp for _ in INFIX]))
    my_contract_dict["pow"] = _c_pow
    my_contract_dict["neg"] = _c_neg
    my_contract_dict["or"] = _contract_sexp
    my_contract_dict["and"] = _contract_sexp
    my_contract_dict["not"] = _contract_sexp
    my_contract_dict["Constrain"] = _c_constrain

    lines = list()

    # Translate constraints
    for c in constraints:
        cons = walk(my_expand_dict, my_contract_dict, c, None)
        lines.append("".join(cons))

    if len(lines) == 0:
        final = ""
    elif len(lines) == 1:
        final = lines[0]
    else:
        final = "(and {})".format(" ".join(lines))

    logger("smt2 query:\n{}", final)

    return final


def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input
        from function_to_lexed import function_to_lexed
        from lexed_to_parsed import lexed_to_parsed
        from pass_lift_inputs_and_inline_assigns import \
            pass_lift_inputs_and_inline_assigns
        from pass_simplify import pass_simplify
        from pass_reverse_diff import pass_reverse_diff
        from pass_lift_consts import pass_lift_consts
        from pass_single_assignment import pass_single_assignment

        data = get_runmain_input(argv)
        logging.set_log_level(logging.NONE)

        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)
        exp, constraints, inputs = pass_lift_inputs_and_inline_assigns(tree)

        logging.set_log_level(logging.HIGH)
        smt2 = output_smt2(constraints)


        for i in inputs:
            print("(declare-fun {} () Real)".format(i))

        for i, domain in inputs.items():
            print("(assert (<= {} {}))".format(domain[1][1], i))
            print("(assert (<= {} {}))".format(domain[2][1], i))

        print(smt2)

        print("(check-sat)")
        print("(exit)")

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
