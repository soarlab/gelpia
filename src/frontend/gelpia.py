#!/usr/bin/env python3

import color_printing
import logging

import argument_parser
import color_printer as color
import logging




PYTHON_DIR = path.abspath(path.dirname(__file__))
GIT_DIR = path.split(PYTHON_DIR)[0]
SRC_DIR = path.join(GIT_DIR, "src")
BIN_DIR = path.join(GIT_DIR, "bin")
if PYTHON_DIR != BIN_DIR:
    logging.error("gelpia.py should not be run directly from src")


gelpia_logger = logging.make_module_logger(color.blue("gelpia_main"))



def mk_file_hash(function):
    h  = hash(function)
    h *= hash(time.time())
    h *= os.getpid()
    return hex(h % (1 << 48))[2:] # Trim 0x


def append_to_environ(pathname, addition):
    try:
        current = os.environ[pathname]
        if addition in current:
            return
        os.environ[pathname] = "{}:{}".format(addition, current)
        gelpia_logger(logging.HIGH, "  {} = {}",
                      pathname, os.environ[pathname]))
    except KeyError:
        os.environ[pathname] = addition
        gelpia_logger(logging.HIGH, "  new {} = {}",
                      pathname, os.environ[pathname]))


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
    gelpia_logger(logging.MEDIUM, "Adding to ENV")

    path_addition = path.join(git_dir, "requirements/bin")
    append_to_environ("PATH", path_addition)

    ld_lib_addition = path.join(git_dir, "requirements/lib")
    append_to_environ("LD_LIBRARY_PATH", ld_lib_addition)

    lib_addition = path.join(git_dir, "requirements/lib")
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
    executable = path.join(base_dir, "target/{}/cooperative".format(name))

    return executable


def write_rust_function(rust_function):
    file_id = hash_string(rust_function)
    filename = path.join(src_dir, "func/src/lib_generated_{}.rs".format(file_id))

    try:
        with open(filename, "w") as f:
            f.write(rust_function)
    except OSError:
        logging.error("Cannot open '{}'", filename)
        sys.exit(-1)

    return file_id


def find_max(function, epsilons, timeout, update, iters, seed, debug):
    input_epsilon, output_epsilon, output_epsilon_relative = epsilons
    inputs, consts, rust_function, interp_function = process_function(function)

    file_id = write_rust_function(rust_function)

    executable_args = ["-c", "[" + "]|[".join(consts.values()) + "]",
                       "-f", interp_function,
                       "-i", "[" + "]|[".join(inputs.values()) + "]",
                       "-x", input_epsilon,
                       "-y", output_epsilon,
                       "-r", output_epsilon_relative,
                       "-S", "generated_"+file_id,
                       "-n", ",".join(inputs.keys()),
                       "-t", timeout,
                       "-u", update,
                       "-M", iters,
                       "--seed", seed,
                       "-d" if debug else "",
                       "-L" if logging.get_log_level() >= logging.HIGH else "",]

    answer_lines = []
    for line in iu.run_async(executable, executable_args):
        if line.startswith("lb:"):
            gelpia_logger(logging.HIGH, line)
        else:
            answer_lines.append(line.strip())

    to_delete = [".compiled/libfunc_generated_"+file_id+".so",
                 "func/target/release/libfunc_generated_"+file_id+".so",
                 "func/target/release/func_generated_"+file_id+".d",]
    to_delete = [path.join(src_dir, f) for f in to_delete]
    for f in to_delete:
        try:
            os.remove(f)
        except:
            pass

    try:
        output = " ".join(answer_lines)
        idx = output.find('[')
        output = output[idx:]
        lst = eval(output, {'inf':float('inf')})
        assert(type(lst[-1]) is dict)
        for k in list(lst[-1]):
            if k[0] == "$":
                del lst[-1][k]
    except:
        logging.error("Unable to parse rust solver's output: {}", output)
        sys.exit(-1)

    max_lower = lst[0][0]
    max_upper = lst[0][1]

    domain = lst[-1]
    for inp in inputs:
        if inp in domain.keys():
            gelpia_logger(logging.LOW, "  {} in {}", inp, domain[inp])
        else:
            gelpia_logger(logging.LOW, "  {} in any", inp)

    return max_lower, max_upper, domain


def main(argv):
    args = argument_parser.parse_args(argv)

    logging.set_log_level(args.verbose)
    logging.set_log_filename(args.log_file)

    setup_requirements(GIT_DIR)
    rust_executable = setup_rust_env(GIT_DIR, args.debug)

    max_lower, max_upper, domain = find_max(args.function,
                                            (args.input_epsilon,
                                             args.output_epsilon,
                                             args.output_epsilon_relative),
                                            args.timeout,
                                            args.update,
                                            args.max_iters,
                                            args.seed,
                                            args.debug)
    print("Maximum is in [{}, {}]".format(max_lower, max_upper))
    return 0







if __name__ == "__main__":
    sys.exit(main(sys.argv))
