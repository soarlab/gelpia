#!/usr/bin/env python3

import argparse
import ast

import ian_utils as iu

from parsed_input_lift_pass import *
from parsed_constant_lift_pass import *
from parsed_div_zero_pass import *

from lifted_to_rust import *
from lifted_to_interpreter import *

def parse_args():
    """ Command line argument parser. Returns a dict from arg name to value"""

    # Using the Ian argument parser since it has nicer from file characteristics
    arg_parser = iu.IanArgumentParser(description="Global function optimizer based "
                                  "on branch and bound for noncontinuous "
                                  "functions.",
                                  fromfile_prefix_chars='@')
    # Verbosity level
    arg_parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        type=int, default=0)
    arg_parser.add_argument("-ie", "--input-epsilon",
                        help="cuttoff for function input size",
                        type=float, default=.001)
    arg_parser.add_argument("-oe", "--output-epsilon",
                        help="cuttoff for function output size",
                        type=float, default=.001)
    arg_parser.add_argument("-i", "--input",
                        help="Search space. "
                        "Format is: {V1 : (inf_V1, sup_V1), ...}"
                        "Where V1 is the interval name, inf_V1 is the infimum, "
                        "and sup_V1 is the supremum",
                        type=str, nargs='+', required=True,)
    arg_parser.add_argument("-f", "--function",
                        help="the c++ interval arithmatic function to evaluate",
                        type=str, nargs='+', required=True,)
    arg_parser.add_argument("-d", "--debug",
                        help="Debug run of function. Makes the minimum verbosity"
                        " level one. Runs a debug build of gelpia, "
                        "with backtrace enabled.", action="store_true")
    arg_parser.add_argument("-t", "--timeout",
                        type=int, help="Timeout for execution in seconds.",
                        default=0)
    arg_parser.add_argument("-u", "--update",
                        type=int, help="Time between update thread executions.",
                        default=10)
    arg_parser.add_argument("-L", "--logging",
                        help="Enable solver logging to stderr",
                        type=str, nargs='?', const=True, default=None)

    # actually parse
    args = arg_parser.parse_args()

    # set verbosity level
    if args.debug or args.verbose:
        iu.set_log_level(max(1, args.verbose))

    # grab function (this is required since the function may have spaces in it)
    function = ' '.join(args.function)
    inputs = ' '.join(args.input)

    start = parse_input_box(inputs)

    exp = function_parser.parse(start+'\n'+function)
    inputs = lift_inputs(exp)
    consts = lift_constants(exp, inputs)
    
    rust_func, new_inputs, new_consts = translate_rust(exp, consts, inputs)
    interp_func, _, __ = translate_interp(exp, consts, inputs)

    divides_by_zero = div_by_zero(exp, new_inputs, new_consts)
    
    if divides_by_zero:
        print("[inf, {\nunknown}]")
        sys.exit(-2)
                     
    return {"input_epsilon"   : args.input_epsilon,
            "output_epsilon"  : args.output_epsilon,
            "inputs"          : new_inputs,
            "constants"       : '|'.join(new_consts),
            "rust_function"   : rust_func,
            "interp_function" : interp_func,
            "expression"      : exp,
            "debug"           : args.debug,
            "timeout"         : args.timeout,
            "update"          : args.update,
            "logfile"         : args.logging,}


def parse_input_box(box_string):
    inputs = ast.literal_eval(box_string)
    reformatted = list()
    for k,v in inputs.items():
        reformatted.append("{} = [{},{}];".format(k, *v))
    return '\n'.join(reformatted)
    
