

import sys

from expression_walker import walk
from pass_utils import BINOPS, UNOPS
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.cyan("single_assignment"),
                                    logging.HIGH)


def pass_single_assignment(exp, inputs):
    """ Converts the expression to single assignment form """

    PASSTHROUGH = {
        "Const",
        "ConstantInterval",
        "Float",
        "Input",
        "Integer",
    }
    UNCACHED = PASSTHROUGH.union({"Tuple", "Variable"})

    def cache(exp, hashed=dict()):
        if exp[0] in UNCACHED:
            return exp
        try:
            key = hashed[exp]
            assert(logger("Eliminated redundant subexpression : {}", exp))
        except KeyError:
            key = "_expr_" + str(len(hashed))
            hashed[exp] = key
            assigns[key] = exp
        return ("Variable", key)

    def _two_items(work_stack, count, args):
        assert(len(args) == 3)
        left = cache(args[1])
        right = cache(args[2])
        work_stack.append((True, count, (args[0], left, right)))

    def _one_item(work_stack, count, args):
        assert(len(args) == 2)
        arg = cache(args[1])
        work_stack.append((True, count, (args[0], arg)))

    def _many_items(work_stack, count, args):
        args = [args[0]] + [cache(sub) for sub in args[1:]]
        work_stack.append((True, count, tuple(args)))

    my_contract_dict = dict()
    my_contract_dict.update(zip(BINOPS, [_two_items for _ in BINOPS]))
    my_contract_dict.update(zip(UNOPS,  [_one_item for _ in UNOPS]))
    my_contract_dict["Tuple"] = _two_items
    my_contract_dict["Box"] = _many_items

    assigns = dict()
    exp = walk(dict(), my_contract_dict, exp, assigns)

    return exp, assigns


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

        data = get_runmain_input(argv)
        logging.set_log_level(logging.NONE)

        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)
        exp, inputs = pass_lift_inputs_and_inline_assigns(tree)
        exp = pass_simplify(exp, inputs)
        d, diff_exp = pass_reverse_diff(exp, inputs)
        diff_exp = pass_simplify(diff_exp, inputs)
        c, diff_exp, consts = pass_lift_consts(diff_exp, inputs)

        logging.set_log_level(logging.HIGH)
        logger("raw: \n{}\n", data)
        diff_exp, assigns = pass_single_assignment(diff_exp, inputs)

        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("consts:")
        for name, val in consts.items():
            logger("  {} = {}", name, val)
        logger("assigns:")
        for name, val in assigns.items():
            logger("  {} = {}", name, val)
        logger("expression:")
        logger("  {}", exp)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
