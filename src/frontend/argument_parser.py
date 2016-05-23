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
    exe = path.basename(sys.argv[0])
    if exe == "gelpia":
        return parse_gelpia_args()
    elif exe == "dop_gelpia":
        return parse_dop_args()
    else:
        print("Defaulting to gelpia argument parsing")
        return parse_gelpia_args()


def parse_gelpia_args():
    """ Command line argument parser. Returns a dict from arg name to value"""

    # Using the Ian argument parser since it has nicer from file characteristics
    arg_parser = iu.IanArgumentParser(description="Global function optimizer based "
                                  "on branch and bound for noncontinuous "
                                  "functions.",
                                  fromfile_prefix_chars='@')
    arg_parser.add_argument("--dreal", action='store_const', const=True, default=False)
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
    arg_parser.add_argument("-g", "--grace",
                        type=int, help="Grace period for timeout option. Defaults to twice the supplied timeout",
                        default=0)
    arg_parser.add_argument("-u", "--update",
                        type=int, help="Time between update thread executions.",
                        default=10)
    arg_parser.add_argument("-L", "--logging",
                        help="Enable solver logging to stderr",
                        type=str, nargs='?', const=True, default=None)
    arg_parser.add_argument("-z", "--skip-div-zero",
                            action="store_true", help="Skip division by zero check")
    
    # actually parse
    args = arg_parser.parse_args()

    # set verbosity level
    if args.debug or args.verbose:
        iu.set_log_level(max(1, args.verbose))

    # grab function (this is required since the function may have spaces in it)
    function = ' '.join(args.function)
    if args.dreal:
        function = "-({})".format(function)
    inputs = ' '.join(args.input)

    start = parse_input_box(inputs)

    exp = function_parser.parse(start+'\n'+function)
    inputs = lift_inputs(exp)
    consts = lift_constants(exp, inputs)
    
    rust_func, new_inputs, new_consts = translate_rust(exp, consts, inputs)

    if not args.skip_div_zero:
        if div_by_zero(exp, new_inputs, new_consts):
            print("ERROR: Division by zero")
            sys.exit(-2)

    interp_func, _, __ = translate_interp(exp, consts, inputs)
    
    return {"input_epsilon"   : args.input_epsilon,
            "output_epsilon"  : args.output_epsilon,
            "inputs"          : new_inputs,
            "constants"       : '|'.join(new_consts),
            "rust_function"   : rust_func,
            "interp_function" : interp_func,
            "expression"      : exp,
            "debug"           : args.debug,
            "timeout"         : args.timeout,
            "grace"           : args.grace,
            "update"          : args.update,
            "logfile"         : args.logging,
            "dreal"           : args.dreal}


def parse_input_box(box_string):
    inputs = ast.literal_eval(box_string)
    reformatted = list()
    for k,v in inputs.items():
        reformatted.append("{} = [{},{}];".format(k, *v))
    return '\n'.join(reformatted)
    

def parse_dop_args():
    arg_parser = argparse.ArgumentParser(description="Gelpia which reads a subset of the dop query format")
    arg_parser.add_argument("query_file",type=str)
    arg_parser.add_argument("--dreal", action='store_const', const=True, default=False)
    arg_parser.add_argument("-d", "--debug",
                        help="Debug run of function. Makes the minimum verbosity"
                        " level one. Runs a debug build of gelpia, "
                        "with backtrace enabled.", action="store_true")
    arg_parser.add_argument("-t", "--timeout",
                        type=int, help="Timeout for execution in seconds.",
                        default=0)
    arg_parser.add_argument("-g", "--grace",
                        type=int, help="Grace period for timeout option. Defaults to twice the supplied timeout",
                        default=0)
    arg_parser.add_argument("-u", "--update",
                        type=int, help="Time between update thread executions.",
                        default=10)
    arg_parser.add_argument("-L", "--logging",
                        help="Enable solver logging to stderr",
                        type=str, nargs='?', const=True, default=None)
    arg_parser.add_argument("-v", "--verbose", help="increase output verbosity",
                            type=int, default=0)
    arg_parser.add_argument("-z", "--skip-div-zero",
                            action="store_true", help="Skip division by zero check")
    
    args = arg_parser.parse_args()
    with open(args.query_file, 'r') as f:
        query = f.read()

    # set verbosity level
    if args.debug or args.verbose:
        iu.set_log_level(max(1, args.verbose))
        
    # precision
    match = re.match(r"^prec: +(\d*.\d*) *$", query)
    if match:
        prec = float(match.group(1))
    else:
        prec = 0.001

    # vars
    lines = [line.strip() for line in query.splitlines() if line.strip()!=''and line.strip()[0] != '#']
    try:
        start = lines.index("var:")
    except:
        print("Malformed query file, no var section: {}".format(args.query_file))
        sys.exit(-1)
    var_lines = list()
    for line in lines[start+1:]:
        if ':' in line:
            break
        match = re.search(r"(\[[^,]+, *[^\]]+\]) *([^;]+)", line)
        if match:
            val = match.group(1)
            name = match.group(2)
        else:
            print("Malformed query file, imporoper var: {}".format(line))
            sys.exit(-1)
        var_lines.append("{} = {};".format(name, val))
    var_lines = '\n'.join(var_lines)
        
    # cost
    try:
        start = lines.index("cost:")
    except:
        print("Malformed query file, no cost section: {}".format(args.query_file))
        sys.exit(-1)
    function = list()
    for line in lines[start+1:]:
        if ':' in line:
            break
        function.append("({})".format(line.replace(';','')))
    function = '+'.join(function)
    if args.dreal:
        function = "-({})".format(function)
    
    # constraints
    try:
        start = lines.index("ctr:")
    except:
        start = False

    constraints = list()
    if start:
        for line in lines[start+1:]:
            if ':' in line:
                break
            constraints.append(line)
        print("Gelpia does not currently handle constraints")
        sys.exit(-1)

    constraints = '\n'.join(constraints)

    # combining and parsing
    reformatted_query = '\n'.join((var_lines, constraints, function))

    exp = function_parser.parse(reformatted_query)

    inputs = lift_inputs(exp)
    consts = lift_constants(exp, inputs)
    
    rust_func, new_inputs, new_consts = translate_rust(exp, consts, inputs)

    if not args.skip_div_zero:
        if div_by_zero(exp, new_inputs, new_consts):
            print("ERROR: Division by zero")
            sys.exit(-2)

    interp_func, _, __ = translate_interp(exp, consts, inputs)
    
    return {"input_epsilon"   : prec,
            "output_epsilon"  : prec,
            "inputs"          : new_inputs,
            "constants"       : '|'.join(new_consts),
            "rust_function"   : rust_func,
            "interp_function" : interp_func,
            "expression"      : exp,
            "debug"           : args.debug,
            "timeout"         : args.timeout,
            "grace"           : args.grace,
            "update"          : args.update,
            "logfile"         : args.logging,
            "dreal"           : args.dreal}

    
