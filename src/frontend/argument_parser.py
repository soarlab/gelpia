#!/usr/bin/env python3

import argparse
import ast

import ian_utils as iu
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

    exp = parser.parse(function)
    lift_constants(exp)

    rust_func, _, __, = translate_rust(exp)
    interp_func, var, const = translate_interp(exp)
    parse_input_box(inputs)
                     
    return {"input_epsilon"   : args.input_epsilon,
            "output_epsilon"  : args.output_epsilon,
            "inputs"          : [(name, GLOBAL_BINDINGS[name]) for name in GLOBAL_INPUTS_LIST],
            "constants"       : '|'.join(const),
            "rust_function"   : rust_func,
            "interp_function" : interp_func,
            "bindings"        : {k:v for k,v in GLOBAL_BINDINGS.items() if type(v) != tuple},
            "debug"           : args.debug,
            "timeout"         : args.timeout,
            "update"          : args.update,
            "logfile"         : args.logging}


def parse_input_box(box_string):
    inputs = ast.literal_eval(box_string)
    for k in [k for k,v in GLOBAL_BINDINGS.items() if v == None]:
        GLOBAL_BINDINGS[k] = inputs[k]
