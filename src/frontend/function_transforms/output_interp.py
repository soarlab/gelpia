

import sys

from expression_walker import walk
from pass_utils import INFIX, UNOPS
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.cyan("output_interp"),
                                    logging.HIGH)


def output_interp(exp, inputs, consts):

    input_mapping = {name: str(i) for name, i in zip(inputs, range(len(inputs)))}
    const_mapping = {name: str(i) for name, i in zip(consts, range(len(consts)))}

    def _const(work_stack, count, exp):
        assert(exp[0] == "Const")
        assert(len(exp) == 2)
        work_stack.append((True, count,  ['c' + str(const_mapping[exp[1]])]))

    def _input(work_stack, count, exp):
        assert(exp[0] == "Input")
        assert(len(exp) == 2)
        work_stack.append((True, count,  ['i' + str(input_mapping[exp[1]])]))

    my_expand_dict = {"Const": _const,
                      "Input": _input}

    def _pow(work_stack, count, args):
        assert(args[0] == "pow")
        assert(len(args) == 3)
        assert(args[2][0] == "Integer")
        assert(type(args[1]) is list)
        work_stack.append((True, count, args[1] + ["p" + args[2][1]]))

    def _sub2(work_stack, count, args):
        assert(args[0] == "sub2")
        assert(len(args) == 3)
        assert(type(args[1]) is list)
        assert(type(args[2]) is list)
        work_stack.append((True, count, args[1] + args[2] + ["osub2"]))

    def _powi(work_stack, count, args):
        assert(args[0] == "powi")
        assert(len(args) == 3)
        assert(type(args[1]) is list)
        assert(type(args[2]) is list)
        work_stack.append((True, count, args[1] + args[2] + ["op"]))

    def _infix(work_stack, count, args):
        assert(args[0] in INFIX)
        assert(len(args) == 3)
        assert(type(args[1]) is list)
        assert(type(args[2]) is list)
        work_stack.append((True, count, args[1] + args[2] + ["o" + args[0]]))

    def _unops(work_stack, count, args):
        assert(args[0] in UNOPS)
        assert(len(args) == 2)
        assert(type(args[1]) is list)
        work_stack.append((True, count, args[1] + ["f" + args[0].lower()]))

    def _return(work_stack, count, args):
        assert(args[0] == "Return")
        assert(len(args) == 2)
        return args[1]

    my_contract_dict = dict()
    my_contract_dict.update(zip(INFIX, [_infix for _ in INFIX]))
    my_contract_dict.update(zip(UNOPS, [_unops for _ in UNOPS]))
    my_contract_dict["pow"] = _pow
    my_contract_dict["powi"] = _powi
    my_contract_dict["sub2"] = _sub2
    my_contract_dict["Return"] = _return

    exp = walk(my_expand_dict, my_contract_dict, exp)

    return ','.join(exp)


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
        logger("  {}", diff_exp)

        interp_function = output_interp(exp, inputs, consts)

        logger("interp_function: \n{}", interp_function)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
