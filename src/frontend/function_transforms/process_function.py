

import sys
import collections

from pass_utils import extract_exp_from_diff
from function_to_lexed import function_to_lexed
from lexed_to_parsed import lexed_to_parsed
from pass_lift_inputs_and_inline_assigns import \
    pass_lift_inputs_and_inline_assigns
from pass_simplify import pass_simplify
from pass_reverse_diff import pass_reverse_diff
from pass_lift_consts import pass_lift_consts
from pass_single_assignment import pass_single_assignment
from output_rust import output_rust
from output_interp import output_interp
from output_flatten import output_flatten
try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color
logger = logging.make_module_logger(color.cyan("process_function"),
                                    logging.HIGH)

def process_function(data, invert=False):
    tokens = function_to_lexed(data)
    tree = lexed_to_parsed(tokens)
    exp, constraints, inputs = pass_lift_inputs_and_inline_assigns(tree)
    if invert:
        exp = ("neg", exp[1])
    exp = pass_simplify(exp, inputs)
    d, diff_exp = pass_reverse_diff(exp, inputs)
    diff_exp = pass_simplify(diff_exp, inputs)
    c, diff_exp, consts = pass_lift_consts(diff_exp, inputs)
    sa_exp, assigns = pass_single_assignment(diff_exp, inputs)
    rust_function = output_rust(sa_exp, inputs, consts, assigns)
    exp = extract_exp_from_diff(diff_exp)
    interp_function = output_interp(exp, inputs, consts)
    flat_consts = collections.OrderedDict()
    for name, const in consts.items():
        flat_consts[name] = output_flatten(const)
    flat_inputs = collections.OrderedDict()
    for name, input in inputs.items():
        flat_inputs[name] = output_flatten(input)
    return flat_inputs, flat_consts, rust_function, interp_function


def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from pass_utils import get_runmain_input
        data = get_runmain_input(argv)
        inputs, consts, rust_function, interp_function = process_function(data)

        logger("raw: \n{}\n", data)
        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("consts:")
        for name, val in consts.items():
            logger("  {} = {}", name, val)
        logger("Rust function:\n{}\n", rust_function)
        logger("Interp function:\n{}\n", interp_function)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
