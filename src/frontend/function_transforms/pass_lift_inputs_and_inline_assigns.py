

import sys
from collections import OrderedDict

from expression_walker import walk
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.cyan("lift_inputs_and_inline_assigns"),
                                    logging.HIGH)


def pass_lift_inputs_and_inline_assigns(exp):
    """ Extracts input variables from an expression and inlines assignments"""

    # Function local variables
    assigns = dict()         # name -> expression
    used_assigns = set()          # assignments seen in the main exp
    inputs = OrderedDict()  # name -> input range
    used_inputs = set()          # inputs seen in the main exp

    def _input_interval(work_stack, count, exp):
        assert(exp[0] == "InputInterval")
        assert(len(exp) == 3)
        # Here is where implicit inputs should be lifted if/when we decide to
        ret = ("ConstantInterval", exp[1], exp[2])
        work_stack.append((True, count, ret))

    def _name(work_stack, count, exp):
        assert(exp[0] == "Name")
        assert(len(exp) == 2)

        if exp[1] in inputs:
            assert(exp[1] not in assigns)
            used_inputs.add(exp[1])
            ret = ("Input", exp[1])
            work_stack.append((True, count, ret))
            return

        if exp[1] in assigns:
            assert(exp[1] not in inputs)
            used_assigns.add(exp[1])
            ret = assigns[exp[1]]
            work_stack.append((True,  count, ret))
            assert(logger("inlined {}", exp[1]))
            return

        logger.error("Use of undeclared name: {}", exp[1])
        sys.exit(-1)

    # A leading tuple must be an assign
    while type(exp[0]) is tuple:
        assignment = exp[0]
        assert(assignment[0] == "Assign")
        name = assignment[1]
        assert(name[0] == "Name")
        val = assignment[2]

        if name[1] in inputs or name[1] in assigns:
            logger.error("Variable assigned to twice: {}", name[1])
            sys.exit(-1)

        if val[0] == "InputInterval":
            inputs[name[1]] = val
            assert(logger("Found input {} = {}", name[1], val))
        else:
            assigns[name[1]] = val
            assert(logger("Found assign {} = {}", name[1], val))

        # Work on the rest of the expression
        exp = exp[1]

    my_expand_dict = {"InputInterval": _input_interval,
                      "Name":          _name}

    new_exp = walk(my_expand_dict, dict(), exp, assigns)

    return new_exp, inputs


def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input
        from function_to_lexed import function_to_lexed
        from lexed_to_parsed import lexed_to_parsed

        data = get_runmain_input(argv)

        logging.set_log_level(logging.NONE)
        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)

        logging.set_log_level(logging.HIGH)
        logger("raw: \n{}\n", data)
        exp, inputs = pass_lift_inputs_and_inline_assigns(tree)

        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("expression:\n{}\n", exp)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
