#!/usr/bin/env python3

import argument_parser
import color_printing as color
import gelpia_logging as logging
import ian_utils as iu
from process_function import process_function

import os
import os.path as path
import re
import sys
import time
from multiprocessing import Process, Value

logger = logging.make_module_logger(color.cyan("gelpia_main"))


PYTHON_DIR = path.abspath(path.dirname(__file__))
GIT_DIR = path.split(PYTHON_DIR)[0]
SRC_DIR = path.join(GIT_DIR, "src")
BIN_DIR = path.join(GIT_DIR, "bin")
if PYTHON_DIR != BIN_DIR:
    logger.error("gelpia.py should not be run directly from src")


def hash_string(function):
    h = hash(function)
    h *= hash(time.time())
    h *= os.getpid()
    return hex(h % (1 << 48))[2:]  # Trim 0x


def append_to_environ(pathname, addition):
    try:
        current = os.environ[pathname]
        # if addition in current:
        #     return
        os.environ[pathname] = "{}:{}".format(addition, current)
        logger(logging.HIGH, "  {} = {}", pathname, os.environ[pathname])
    except KeyError:
        os.environ[pathname] = addition
        logger(logging.HIGH, "  new {} = {}", pathname, os.environ[pathname])


def run_once(f):
    def wrapper(*args, **kwargs):
        if wrapper.has_run:
            logging.error("Function '{}' should only be called once"
                          .format(f.__name__))
            return None
        wrapper.has_run = True
        return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


@run_once
def setup_requirements(git_dir):
    logger(logging.MEDIUM, "Adding to ENV")

    path_addition = path.join(git_dir, "requirements/bin")
    append_to_environ("PATH", path_addition)

    ld_lib_addition = path.join(git_dir, "requirements/lib")
    append_to_environ("LD_LIBRARY_PATH", ld_lib_addition)

    lib_addition = path.join(git_dir, "requirements/lib")
    append_to_environ("LIBRARY_PATH", lib_addition)

    ld_lib_addition = path.join(git_dir, "requirements/lib/rustlib/x86_64-unknown-linux-gnu/lib/")
    append_to_environ("LD_LIBRARY_PATH", ld_lib_addition)

    lib_addition = path.join(git_dir, "/requirements/lib/rustlib/x86_64-unknown-linux-gnu/lib/")
    append_to_environ("LIBRARY_PATH", lib_addition)

    c_inc_addition = path.join(git_dir, "requirements/include")
    append_to_environ("C_INCLUDE_PATH", c_inc_addition)

    cplus_inc_addition = path.join(git_dir, "requirements/include")
    append_to_environ("CPLUS_INCLUDE_PATH", cplus_inc_addition)


@run_once
def setup_rust_env(git_dir, debug):
    append_to_environ("LD_LIBRARY_PATH", path.join(git_dir, ".compiled"))

    if debug:
        name = "debug"
        append_to_environ("RUST_BACKTRACE", "1")
    else:
        name = "release"

    append_to_environ("LD_LIBRARY_PATH",
                      path.join(git_dir, "src/func/target/{}".format(name)))
    append_to_environ("LD_LIBRARY_PATH",
                      path.join(git_dir, "target/{}/deps".format(name)))

    cooperative = path.join(git_dir, "target/{}/cooperative".format(name))

    return cooperative


def write_rust_function(rust_function, src_dir):
    file_id = hash_string(rust_function)
    filename = path.join(src_dir, "func/src/lib_generated_{}.rs".format(file_id))

    try:
        with open(filename, "w") as f:
            f.write(rust_function)
    except OSError:
        logging.error("Cannot open '{}'", filename)
        sys.exit(-1)

    return file_id


def _find_max(inputs, consts, rust_function,
              interp_function, smt2, file_id, epsilons, timeout,
              grace, update, iters, seed, debug, use_z3, src_dir,
              executable):
    input_epsilon, output_epsilon, output_epsilon_relative, dreal_epsilon, dreal_epsilon_relative = epsilons
    stdout_args = ["|".join(inputs.values()),
                   ",".join(inputs.keys()),
                   "|".join(consts.values()),
                   interp_function,
                   smt2]
    executable_args = ["-x", str(input_epsilon),
                       "-y", str(output_epsilon),
                       "-r", str(output_epsilon_relative),
                       "-Y", str(dreal_epsilon),
                       "-R", str(dreal_epsilon_relative),
                       "-S", "generated_"+file_id,
                       "-t", str(timeout),
                       "-u", str(update),
                       "-M", str(iters),
                       "--seed", str(seed),
                       "-d" if debug else "",
                       "-z" if use_z3 else "",
                       "-L" if logging.get_log_level() >= logging.HIGH else ""]

    assert(logger(logging.MEDIUM, "calling '{} {}'", executable, executable_args))
    assert(logger(logging.MEDIUM, "stdout args:\n{}", stdout_args))
    answer_lines = []
    solver_calls = 0
    max_lower = None
    max_upper = None
    if grace == 0:
        timeout = 2*timeout
    else:
        timeout += grace
    for line in iu.run_async(executable, stdout_args, executable_args, timeout):
        line = line.strip()
        if line == "":
            continue
        logger(logging.MEDIUM, "rust_solver_output: {}", line)
        if line.startswith("lb:"):
            match = re.match(r"lb: ([^,]*), possible ub: ([^,]*), guaranteed ub: ([^,]*)", line)
            max_lower = match.groups(1)
            max_upper = match.groups(3)
        elif line.startswith("debug:") or line.startswith("Stopping") or "panicked" in line or "RUST_BACKTRACE=1" in line or line.startswith("(stdin)"):
            pass
        elif line.startswith("SolverCalls"):
            solver_calls += int(line.split(":")[1])
        else:
            answer_lines.append(line)

    to_delete = [
        path.join(GIT_DIR, ".compiled", "libfunc_generated_"+file_id+".so"),
        path.join(SRC_DIR, "func", "target", "release", "libfunc_generated_"+file_id+".so"),
        path.join(SRC_DIR, "func", "target", "release", "func_generated_"+file_id+".d"),
        path.join(SRC_DIR, "func", "src", "lib_generated_"+file_id+".rs"),
    ]
    to_delete = [path.join(src_dir, f) for f in to_delete]
    for f in to_delete:
        try:
            os.remove(f)
        except:
            pass

    output = " ".join(answer_lines)

    if output == "Overconstrained":
        return output, output, None, solver_calls

    try:
        idx = output.find('[')
        output = output[idx:]
        lst = eval(output, {'inf': float('inf')})
        assert(type(lst[-1]) is dict)
        for k in list(lst[-1]):
            if k[0] == "$":
                del lst[-1][k]
        max_lower = lst[0][0]
        max_upper = lst[0][1]
        domain = lst[-1]

    except Exception as e:
        logging.error("Python exception {}", e)
        if max_lower is None:
            logging.error("Unable to parse rust solver's output: <{}>", output)
            sys.exit(-1)
        raise e


    for inp in inputs:
        if inp in domain.keys():
            logger(logging.LOW, "  {} in {}", inp, domain[inp])
        else:
            logger(logging.LOW, "  {} in any", inp)

    return max_lower, max_upper, domain, solver_calls


def find_max(function, epsilons, timeout, grace, update, iters, seed, debug, use_z3,
             src_dir, executable, drop_constraints, max_lower=None, max_upper=None, domain=None, solver_calls=None):
    inputs, consts, rust_function, interp_function, smt2 = process_function(function)
    file_id = write_rust_function(rust_function, src_dir)
    if drop_constraints:
        smt2 = ""

    my_max_lower, my_max_upper, my_domain, my_solver_calls = _find_max(inputs, consts, rust_function,
                                                                       interp_function, smt2, file_id, epsilons, timeout,
                                                                       grace, update, iters, seed, debug, use_z3, src_dir,
                                                                       executable)

    if max_lower is not None:
        # Note: this means you can't tell the difference between the answer [0.0, 0.0] and [Overconstrained, Overconstrained] 
        solver_calls.value = my_solver_calls
        if my_max_lower == "Overconstrained":
            max_lower.value = 0.0
            max_upper.value = 0.0
        else:
            max_lower.value = my_max_lower
            max_upper.value = my_max_upper
            for key, value in my_domain.items():
                domain[key] = value

    return my_max_lower, my_max_upper, my_domain, my_solver_calls


def find_min(function, epsilons, timeout, grace, update, iters, seed, debug, use_z3,
             src_dir, executable, drop_constraints):
    inputs, consts, rust_function, interp_function, smt2 = process_function(function, invert=True)
    file_id = write_rust_function(rust_function, src_dir)
    if drop_constraints:
        smt2 = ""

    max_lower, max_upper, domain, solver_calls = _find_max(inputs, consts, rust_function,
                                             interp_function, smt2, file_id, epsilons, timeout,
                                             grace, update, iters, seed, debug, use_z3, src_dir,
                                             executable)
    if type(max_lower) == str:
        return max_lower, max_upper, solver_calls

    min_lower = -max_upper
    min_upper = -max_lower
    return min_lower, min_upper, domain, solver_calls


def main(argv):
    args = argument_parser.parse_args(argv)

    logging.set_log_level(args.verbose)
    logging.set_log_filename(args.log_file)

    setup_requirements(GIT_DIR)
    cooperative = setup_rust_env(GIT_DIR, args.debug)

    if args.mode == "min":
        min_lower, min_upper, domain, solver_calls = find_min(args.function,
                                        (args.input_epsilon,
                                         args.output_epsilon,
                                         args.output_epsilon_relative,
                                         args.dreal_epsilon,
                                         args.dreal_epsilon_relative),
                                        args.timeout,
                                        args.grace,
                                        args.update,
                                        args.max_iters,
                                        args.seed,
                                        args.debug,
                                        args.use_z3,
                                        SRC_DIR,
                                        cooperative,
                                        args.drop_constraints)
        print("Minimum lower bound {}".format(min_lower))
        print("Minimum upper bound {}".format(min_upper))
        print("Minimum input {}".format(domain))
        print("Solver calls {}".format(solver_calls))
    elif args.mode == "max":
        max_lower, max_upper, domain, solver_calls = find_max(args.function,
                                        (args.input_epsilon,
                                         args.output_epsilon,
                                         args.output_epsilon_relative,
                                         args.dreal_epsilon,
                                         args.dreal_epsilon_relative),
                                        args.timeout,
                                        args.grace,
                                        args.update,
                                        args.max_iters,
                                        args.seed,
                                        args.debug,
                                        args.use_z3,
                                        SRC_DIR,
                                        cooperative,
                                        args.drop_constraints)
        print("Maximum lower bound {}".format(max_lower))
        print("Maximum upper bound {}".format(max_upper))
        print("Maximum input {}".format(domain))
        print("Solver calls {}".format(solver_calls))
    else:
        manager = Manager()
        max_lower = Value("d", float("nan"))
        max_upper = Value("d", float("nan"))
        max_domain = manager.dict()
        max_solver_calls = Value("i", 0)
        p = Process(target=find_max, args=(args.function,
                                           (args.input_epsilon,
                                            args.output_epsilon,
                                            args.output_epsilon_relative,
                                            args.dreal_epsilon,
                                            args.dreal_epsilon_relative),
                                           args.timeout,
                                           args.grace,
                                           args.update,
                                           args.max_iters,
                                           args.seed,
                                           args.debug,
                                           args.use_z3,
                                           SRC_DIR,
                                           cooperative,
                                           args.drop_constraints,
                                           max_lower,
                                           max_upper,
                                           max_domain,
                                           max_solver_calls))
        p.start()
        min_lower, min_upper, min_domain, min_solver_calls = find_min(args.function,
                                        (args.input_epsilon,
                                         args.output_epsilon,
                                         args.output_epsilon_relative,
                                         args.dreal_epsilon,
                                         args.dreal_epsilon_relative),
                                        args.timeout,
                                        args.grace,
                                        args.update,
                                        args.max_iters,
                                        args.seed,
                                        args.debug,
                                        args.use_z3,
                                        SRC_DIR,
                                        cooperative,
                                        args.drop_constraints)
        p.join()
        print("Minimum lower bound {}".format(min_lower))
        print("Minimum upper bound {}".format(min_upper))
        print("Minimum input {}".format(min_domain))
        print("Maximum lower bound {}".format(max_lower.value))
        print("Maximum upper bound {}".format(max_upper.value))
        print("Maximum input {}".format(max_domain))
        print("Solver calls {}".format(min_solver_calls + max_solver_calls.value))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
