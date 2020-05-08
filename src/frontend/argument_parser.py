

import color_printing as color
import gelpia_logging as logging

import argparse
import shlex
import sys


defaults = argparse.Namespace(
    serial=False,
    debug=False,
    verbose="none",
    mode="max",
    timeout=0,
    max_iters=0,
    input_epsilon=0.001,
    output_epsilon=0.001,
    output_epsilon_relative=0,
    seed=0,
    grace=0,
    update=0,
    log_file=None,
    log_query=False,
)


def parse_args(argv):
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(argv[1:])
    file_args = None

    if args.query_file:
        try:
            with open(args.query_file, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            logging.error("File not found '{}'". args.query_file)
            sys.exit(-1)

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != ""]

        function_lines = [line for line in lines if line[0] != "#"]
        function_str = "\n".join(function_lines)

        comments = [line[1:] for line in lines if line[0] == "#"]
        comments = [line.strip() for line in comments]
        comments = [line for line in comments if line[0] == "-"]
        file_argv = list()
        for line in comments:
            file_argv.extend(shlex.split(line))

        file_args = arg_parser.parse_args(["-f", function_str] + file_argv)

    final_args = get_final_args(defaults, args, file_args)

    return final_args


def combine(default, arg, file_arg):
    if arg is not None:
        return arg
    if file_arg is not None:
        return file_arg
    return default


def get_final_args(defaults, args, file_args):
    if file_args is None:
        file_args = args

    args.function = file_args.function

    d = defaults
    a = args
    f = file_args

    final_args = argparse.Namespace(
        function=f.function,
        serial=combine(d.serial,
                       a.serial,
                       f.serial),
        debug=combine(d.debug,
                      a.debug,
                      f.debug),
        verbose=combine(d.verbose,
                        a.verbose,
                        f.verbose),
        mode=combine(d.mode,
                     a.mode,
                     f.mode),
        timeout=combine(d.timeout,
                        a.timeout,
                        f.timeout),
        max_iters=combine(d.max_iters,
                          a.max_iters,
                          f.max_iters),
        input_epsilon=combine(d.input_epsilon,
                              a.input_epsilon,
                              f.input_epsilon),
        output_epsilon=combine(d.output_epsilon,
                               a.output_epsilon,
                               f.output_epsilon),
        output_epsilon_relative=combine(d.output_epsilon_relative,
                                        a.output_epsilon_relative,
                                        f.output_epsilon_relative),
        seed=combine(d.seed,
                     a.seed,
                     f.seed),
        grace=combine(d.grace,
                      a.grace,
                      f.grace),
        update=combine(d.update,
                       a.update,
                       f.update),
        log_file=combine(d.log_file,
                         a.log_file,
                         f.log_file),
        log_query=combine(d.log_query,
                          a.log_query,
                          f.log_query),
    )

    final_args.verbose = logging.LEVELS[final_args.verbose]

    if final_args.debug and final_args.verbose < logging.MEDIUM:
        final_args.verbose = logging.MEDIUM

    return final_args


def log_args(args):
    logger = logging.make_module_logger(color.cyan("argument_parser"),
                                        logging.MEDIUM)
    logger("Argument settings:")
    logger("  serial = {}", args.serial)
    logger("  debug = {}", args.debug)
    logger("  verbose = {}", args.verbose)
    logger("  mode = '{}'", args.mode)
    logger("  timeout = {}", args.timeout)
    logger("  max_iters = {}", args.max_iters)
    logger("  input_epsilon = {}", args.input_epsilon)
    logger("  output_epsilon = {}", args.output_epsilon)
    logger("  output_epsilon_relative = {}", args.output_epsilon_relative)
    logger("  seed = {}", args.seed)
    logger("  grace = {}", args.grace)
    logger("  update = {}", args.update)
    logger("  log_file = {}", args.log_file)
    logger("  log_query = {}", args.log_query)
    logger("  function = '{}'", args.function)


def create_arg_parser():
    arg_parser = argparse.ArgumentParser(description="Global function optimizer")
    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("query_file",
                       nargs="?",
                       help="File containing a query function. Arguments"
                       " for gelpia may be given as '#' prefixed lines in"
                       " the file, one option per line. Command line flags"
                       " override those in the file.")
    group.add_argument("-f", "--function",
                       help="The function to optimize. Uses a modified dop"
                       " format. For examples see the 'examples' directory"
                       " in gelpia's git.")
    arg_parser.add_argument("--serial",
                            action="store_const",
                            const=True,
                            help="Use the serial rust solver."
                            " (default {})".format(defaults.serial))
    arg_parser.add_argument("-d", "--debug",
                            action="store_const",
                            const=True,
                            help="Use debug mode. Verbosity is set to medium and"
                            "the debug build of the rust solver is used."
                            " (default {})".format(defaults.debug))
    arg_parser.add_argument("-v", "--verbose",
                            nargs="?",
                            const="low",
                            choices=["quiet", "none", "low", "medium", "high"],
                            help="Set output verbosity"
                            " (default '{}')".format(defaults.verbose))
    arg_parser.add_argument("-m", "--mode",
                            choices=["min", "max", "min-max"],
                            help="Which mode the optimizer is in"
                            " (default '{}')".format(defaults.mode))
    arg_parser.add_argument("-t", "--timeout",
                            type=int,
                            help="Timeout for gelpia."
                            " (default {})".format(defaults.timeout))
    arg_parser.add_argument("-M", "--max-iters",
                            type=int,
                            help="Maximum number of iterations for the IBBA"
                            " algorithm."
                            " (default {})".format(defaults.max_iters))
    arg_parser.add_argument("-i", "--input-epsilon",
                            type=float,
                            help="Cutoff for function input size."
                            " (default {})".format(defaults.input_epsilon))
    arg_parser.add_argument("-o", "--output-epsilon",
                            type=float,
                            help="Cutoff for function output size."
                            " (default {})".format(defaults.output_epsilon))
    arg_parser.add_argument("-r", "--output-epsilon-relative",
                            type=float,
                            help="Relative cutoff for function output size"
                            " (default {})"
                            .format(defaults.output_epsilon_relative))
    arg_parser.add_argument("-s", "--seed",
                            type=int,
                            help="Seed for the random number generator. A value"
                            " of 0 indicates a default seed is used. A value of"
                            " 1 indicates a seed will be randomly selected. All"
                            " other values define the seed to be used."
                            "(default {})".format(defaults.seed))
    arg_parser.add_argument("-g", "--grace",
                            type=float,
                            help="Grace period used with the timeout option."
                            " The amount of time after the timout that the rust"
                            " solver is given to clear its queue and report a"
                            " final answer. A value of 0 indicates twice the"
                            " supplied timeout."
                            " (default {})".format(defaults.grace))
    arg_parser.add_argument("-u", "--update",
                            type=float,
                            help="Time between update thread executions in the"
                            " rust solver."
                            " (default {})".format(defaults.update))
    arg_parser.add_argument("-l", "--log-file",
                            help="Redirect logging to given file."
                            " (default {})".format(defaults.log_file))
    arg_parser.add_argument("-q", "--log-query",
                            action="store_true",
                            help="Saves a copy of the query for later"
                            " examination/benchmarking."
                            " (default {})".format(defaults.log_query))
    return arg_parser


if __name__ == "__main__":
    logging.set_log_level(logging.HIGH)
    args = parse_args(sys.argv)
    log_args(args)
    sys.exit(0)
