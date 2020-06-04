

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
    assigns = dict()       # name -> expression
    used_assigns = set()   # assignments seen in the main exp
    inputs = OrderedDict() # name -> input range
    used_inputs = set()    # inputs seen in the main exp
    constraints = set()    # constraints
    cost = list()          # all cost expression pieces

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

    my_expand_dict = {"InputInterval": _input_interval,
                      "Name":          _name,
                      "or":            _e_bool_op,
                      "and":           _e_bool_op,
                      "not":           _e_bool_neg,
                      "Constrain":     _e_constrain}

    def _contract(work_stack, count, args):
        work_stack.append((True, count, tuple(args)))

    my_contract_dict = {"or":            _contract,
                        "and":           _contract,
                        "not":           _contract,
                        "Constrain":     _contract}

    # Filter the expression, which is a large tuple
    for part in exp:
        if part[0] == "Assign":
            name = part[1]
            val = part[2]
            if name[1] in inputs or name[1] in assigns:
                logger.error("Variable assigned to twice: {}", name[1])
                sys.exit(-1)

            if name[0] == "SymbolicConst":
                logger("Dropping assign to SymbolicConst: {}", name[1])
                continue

            if val[0] == "InputInterval":
                inputs[name[1]] = val
                assert(logger("Found input {} = {}", name[1], val))
                continue

            assigns[name[1]] = val
            assert(logger("Found assign {} = {}", name[1], val))
            continue

        if part[0] == "Cost":
            cost.append(part[1])
            continue

        if part[0] in {"or", "and", "not", "Constrain"}:
            constraints.add(part)
            continue

        logger.error("Unable to determine part of expressions:\n{}\n", part)
        sys.exit(-1)

    joined_cost = cost[0]
    for c in cost[1:]:
        joined_cost = ("+", joined_cost, c)

    logger("joined cost: {}", joined_cost)

    new_exp = walk(my_expand_dict, dict(), joined_cost, assigns)

    logger("new_exp: {}", new_exp)

    new_constraints = list()
    for cons in constraints:
        logger("Proccesing constraint:\n{}\n", cons)
        new_cons = walk(my_expand_dict, my_contract_dict, cons, assigns)
        new_constraints.append(new_cons)

    return new_exp, new_constraints, inputs


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
        exp, constraints, inputs = pass_lift_inputs_and_inline_assigns(tree)

        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("constraints:")
        for comp, lhs, rhs in constraints:
            logger("  {} {} {}", lhs, comp, rhs)
        logger("expression:\n{}\n", exp)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
