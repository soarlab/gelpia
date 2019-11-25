

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
logger = logging.make_module_logger(color.cyan("lift_consts"),
                                    logging.HIGH)


def pass_lift_consts(exp, inputs):
    """ Extracts constant values from an expression """

    CONST = {"Const", "ConstantInterval", "Integer", "Float", "SymbolicConst"}
    NON_CONST_UNOPS = {"sinh", "cosh", "tanh", "dabs", "datanh", "floor_power2",
                       "sym_interval"}

    consts = dict()
    hashed = dict()

    def make_constant(exp):
        if exp[0] == "Const":
            assert(exp[1] in consts)
            return exp

        try:
            key = hashed[exp]
            assert(logger("Found use of existing const {}", key))

        except KeyError:
            key = "$_const_{}".format(len(hashed))
            assert(exp not in hashed)
            hashed[exp] = key
            assert(key not in consts)
            consts[key] = exp
            assert(logger("Lifting const {} as {}", exp, key))

        return ('Const', key)

    def _expand_positive_atom(work_stack, count, exp):
        work_stack.append((True, count, (*exp, True)))

    def _expand_negative_atom(work_stack, count, exp):
        assert(len(exp) == 2)
        work_stack.append((True, count, (exp[0], exp[1], False)))

    my_expand_dict = dict()
    my_expand_dict.update(zip(CONST, [_expand_positive_atom for _ in CONST]))
    my_expand_dict["Input"] = _expand_negative_atom

    def _pow(work_stack, count, args):
        assert(args[0] == "pow")
        assert(len(args) == 3)
        l, left = args[1][-1], args[1][:-1]
        r, right = args[2][-1], args[2][:-1]
        op = args[0]

        if right[0] != "Integer":
            op = "powi"

        if op == "pow":
            r = False

        # If both are constant don't consolidate yet
        status = False
        if l and r:
            status = True
        # Otherwise consolidate any arguments that are constant
        elif l:
            left = make_constant(left)
        elif r:
            right = make_constant(right)

        work_stack.append((True, count, (op, left, right, status)))

    def _two_item(work_stack, count, args):
        assert(len(args) == 3)
        l, left = args[1][-1], args[1][:-1]
        r, right = args[2][-1], args[2][:-1]
        op = args[0]

        # If both are constant don't consolidate yet
        status = False
        if l and r:
            status = True
        # Otherwise consolidate any arguments that are constant
        elif l:
            left = make_constant(left)
        elif r:
            right = make_constant(right)

        work_stack.append((True, count, (op, left, right, status)))

    def _tuple(work_stack, count, args):
        assert(args[0] == "Tuple")
        assert(len(args) == 3)
        l, left = args[1][-1], args[1][:-1]
        if len(args[2]) == 1:
            r, right = False, args[2]
        else:
            r, right = args[2][-1], args[2][:-1]

        op = args[0]

        if l:
            left = make_constant(left)
        if r:
            right = make_constant(right)

        work_stack.append((True, count, (op, left, right, False)))

    def _one_item(work_stack, count, args):
        assert(len(args) == 2)
        a, arg = args[1][-1], args[1][:-1]
        op = args[0]

        work_stack.append((True, count, (op, arg, a)))

    def _bad_one_item(work_stack, count, args):
        assert(len(args) == 2)
        a, arg = args[1][-1], args[1][:-1]
        op = args[0]
        if a:
            arg = make_constant(arg)
        work_stack.append((True, count, (op, arg, False)))

    def _box(work_stack, count, args):
        assert(args[0] == "Box")
        box = ["Box"]
        for sub in args[1:]:
            p, part = sub[-1], sub[:-1]
            if p:
                part = make_constant(part)
            box.append(part)
        box.append(False)
        work_stack.append((True, count, tuple(box)))

    def _return(work_stack, count, args):
        assert(args[0] == "Return")
        assert(len(args) == 2)
        r, retval = args[1][-1], args[1][:-1]
        if r:
            retval = make_constant(retval)
        return r, ("Return", retval)

    my_contract_dict = dict()
    my_contract_dict.update(zip(BINOPS,
                                [_two_item for _ in BINOPS]))
    my_contract_dict.update(zip(UNOPS,
                                [_one_item for _ in UNOPS]))
    my_contract_dict.update(zip(NON_CONST_UNOPS,
                                [_bad_one_item for _ in NON_CONST_UNOPS]))
    my_contract_dict["Box"] = _box
    my_contract_dict["Tuple"] = _tuple
    my_contract_dict["pow"] = _pow
    my_contract_dict["Return"] = _return

    n, new_exp = walk(my_expand_dict, my_contract_dict, exp)
    assert(n in {True, False})
    assert(type(new_exp) is tuple)
    assert(new_exp[0] not in {True, False})

    return n, new_exp, consts


def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from function_to_lexed import function_to_lexed
        from lexed_to_parsed import lexed_to_parsed
        from pass_lift_inputs_and_inline_assigns import \
            lift_inputs_and_inline_assigns
        from pass_utils import get_runmain_input
        from pass_simplify import simplify
        from pass_reverse_diff import reverse_diff

        data = get_runmain_input(argv)

        logging.set_log_level(logging.NONE)
        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)
        exp, inputs = lift_inputs_and_inline_assigns(tree)
        exp = simplify(exp, inputs)
        d, diff_exp = reverse_diff(exp, inputs)
        diff_exp = simplify(diff_exp, inputs)

        logging.set_log_level(logging.HIGH)
        logger("raw: \n{}\n", data)
        const, exp, consts = pass_lift_consts(diff_exp, inputs)

        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("consts:")
        for name, val in consts.items():
            logger("  {} = {}", name, val)
        logger("expression:")
        logger("  {}", exp)
        logger("is_const: {}", const)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
