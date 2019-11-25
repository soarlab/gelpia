

import sys

from expression_walker import walk
from pass_utils import INFIX, BINOPS, UNOPS, SYMBOLIC_CONSTS
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.cyan("output_flatten"),
                                    logging.HIGH)


def output_flatten(exp, inputs=None, consts=None, assigns=None):

    def _e_variable(work_stack, count, exp):
        assert(logger("expand_variable: {}", exp))
        assert(exp[0] == "Variable")
        assert(len(exp) == 2)
        assert(exp[1] in assigns)
        work_stack.append((False, count, assigns[exp[1]]))

    def _input(work_stack, count, exp):
        assert(logger("expand_input: {}", exp))
        assert(exp[0] == "Input")
        assert(len(exp) == 2)
        work_stack.append((True, count, [exp[1]]))

    def _const(work_stack, count, exp):
        assert(logger("expand_const: {}", exp))
        assert(exp[0] == "Const")
        assert(len(exp) == 2)
        work_stack.append((False, count, consts[exp[1]]))

    def _float(work_stack, count, exp):
        assert(logger("expand_float: {}", exp))
        assert(exp[0] == "Float")
        assert(len(exp) == 2)
        work_stack.append((True, count, ["[", exp[1], "]"]))

    def _integer(work_stack, count, exp):
        assert(logger("expand_integer: {}", exp))
        assert(exp[0] == "Integer")
        assert(len(exp) == 2)
        work_stack.append((True, count, ["[", exp[1], "]"]))

    def _input_interval(work_stack, count, exp):
        assert(logger("expand_input_interval: {}", exp))
        assert(exp[0] == "InputInterval")
        assert(len(exp) == 3)
        work_stack.append((True, count, ["[", exp[1][1], ", ", exp[2][1], "]"]))

    def _symbolic_const(work_stack, count, exp):
        assert(logger("expand_symbolic_const: {}", exp))
        assert(exp[0] == "SymbolicConst")
        assert(len(exp) == 2)
        assert(exp[1] in SYMBOLIC_CONSTS)
        pair = SYMBOLIC_CONSTS[exp[1]]
        work_stack.append((False, count, ("ConstantInterval", pair[0], pair[1])))

    def _constant_interval(work_stack, count, exp):
        assert(logger("expand_constant_interval: {}", exp))
        assert(exp[0] == "ConstantInterval")
        assert(len(exp) == 3)
        work_stack.append((True, count, ["[", exp[1][1], ", ", exp[2][1], "]"]))

    my_expand_dict = {"Input": _input,
                      "Const": _const,
                      "Float": _float,
                      "Integer": _integer,
                      "InputInterval": _input_interval,
                      "SymbolicConst": _symbolic_const,
                      "ConstantInterval": _constant_interval,
                      "Variable": _e_variable}

    def _infix(work_stack, count, args):
        assert(logger("infix: {}", args))
        assert(args[0] in INFIX)
        assert(len(args) == 3)
        op = args[0]
        left = args[1]
        right = args[2]
        ret = ["("] + left + [" ", op, " "] + right + [")"]
        work_stack.append((True, count, ret))

    def _binop(work_stack, count, args):
        assert(logger("binop: {}", args))
        assert(args[0] in BINOPS or args[0] == "powi")
        assert(len(args) == 3)
        op = args[0]
        first = args[1]
        secon = args[2]
        ret = [op, "("] + first + [", "] + secon + [")"]
        work_stack.append((True, count, ret))

    def _pow(work_stack, count, args):
        assert(logger("pow: {}", args))
        assert(args[0] == "pow")
        assert(len(args) == 3)
        base = args[1]
        expo = args[2]
        assert(expo[0] == "Integer")
        ret = ["pow("] + base + [", ", expo[1] + ")"]
        work_stack.append((True, count, ret))

    def _unop(work_stack, count, args):
        assert(logger("unop: {}", args))
        assert(args[0] in UNOPS)
        assert(len(args) == 2)
        op = args[0]
        arg = args[1]
        work_stack.append((True, count, [op, "("] + arg + [")"]))

    def _neg(work_stack, count, args):
        assert(logger("neg: {}", args))
        assert(args[0] == "neg")
        assert(len(args) == 2)
        work_stack.append((True, count, ["-("] + args[1] + [")"]))

    def _box(work_stack, count, args):
        assert(logger("box: {}", args))
        assert(args[0] == "Box")
        if len(args) == 1:
            work_stack.append((True, count, ["None"]))
            return
        box = ["Box("]
        for sub in args[1:]:
            box += sub + [", "]
        box = box[0:-1] + [")"]
        work_stack.append((True, count, box))

    def _tuple(work_stack, count, args):
        assert(logger("tuple: {}", args))
        assert(args[0] == "Tuple")
        assert(len(args) == 3)
        ret = ["Tuple("] + args[1] + [", "] + args[2] + [")"]
        work_stack.append((True, count, ret))

    def _return(work_stack, count, args):
        assert(logger("Return: {}", args))
        assert(args[0] == "Return")
        assert(len(args) == 2)
        return args[1]

    my_contract_dict = dict()
    my_contract_dict.update(zip(BINOPS,
                                [_binop for _ in BINOPS]))
    my_contract_dict.update(zip(UNOPS,
                                [_unop for _ in UNOPS]))
    my_contract_dict.update(zip(INFIX,
                                [_infix for _ in INFIX]))
    my_contract_dict["pow"] = _pow
    my_contract_dict["neg"] = _neg
    my_contract_dict["Box"] = _box
    my_contract_dict["Tuple"] = _tuple
    my_contract_dict["Return"] = _return

    retlist = walk(my_expand_dict, my_contract_dict, exp, assigns)
    retval = "".join(retlist)
    assert(logger("Final output: {}", retval))

    return retval


def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input, extract_exp_from_diff
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
        exp, inputs = pass_lift_inputs_and_inline_assigns(tree)
        exp = pass_simplify(exp, inputs)
        d, diff_exp = pass_reverse_diff(exp, inputs)
        diff_exp = pass_simplify(diff_exp, inputs)
        c, diff_exp, consts = pass_lift_consts(diff_exp, inputs)
        exp = extract_exp_from_diff(diff_exp)

        logging.set_log_level(logging.HIGH)
        logger("raw: \n{}\n", data)
        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("consts:")
        for name, val in consts.items():
            logger("  {} = {}", name, val)
        logger("expression:")
        logger("  {}", exp)

        flat_exp = output_flatten(exp, inputs, consts)

        logger("flat_exp: \n{}", flat_exp)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
