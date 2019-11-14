#!/usr/bin/env python3

import subprocess
import argparse
import shlex
import sys
import time
import threading
import queue


class AsyncReader(threading.Thread):
    def __init__(self, fil, q):
        threading.Thread.__init__(self)
        self.q = q;
        self.fil = fil

    def run(self):
        output = "empty"
        while output != "":
            output = self.fil.readline()
            self.q.put(output)


# popen wrappers
def run(cmd, args_list, error_string="An Error has occured", expected_return=0):
    command = [cmd] + args_list
    should_exit = None
    try:
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:
            output = proc.stdout.read().decode("utf-8")
            proc.wait()

            if (expected_return != None
                and proc.returncode != expected_return):
                error(error_string)
                error("Return code: {}".format(proc.returncode))
                error("Command used: {}".format(command))
                error("Trace:\n{}".format(output))
                should_exit = proc.returncode
    except KeyboardInterrupt:
        raise
    except:
        error("Unable to run given executable, does it exist?")
        error("executable: {}".format(command))
        sys.exit(-1)

    if should_exit != None:
        sys.exit(should_exit)

    return output


def run_async(cmd, args_list, term_time, error_string="An Error has occured",
              expected_return=0):
    command = [cmd] + args_list
    should_exit = None
    try:
        with subprocess.Popen(command,
                              bufsize=1,
                              universal_newlines=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:
            start_time = time.time()

            # Asynchronously collect messages
            stdout_q = queue.Queue();
            stdout_r = AsyncReader(proc.stdout, stdout_q);
            stdout_r.start()

            while proc.poll() is None:
                if not stdout_q.empty():
                    line = stdout_q.get()
                    yield line

                # Kill proc if timeout exceeded
                if term_time is not None:
                    if time.time() > term_time:
                        print("Killed")
                        proc.kill()
                time.sleep(0.1)

            # Clear remaining buffered messages
            while stdout_r.is_alive() or not stdout_q.empty():
                if not stdout_q.empty():
                    yield stdout_q.get()

            proc.wait()
            if (expected_return != None) and (proc.returncode not in
                                              (expected_return, -9)):
                error(error_string)
                error("Return code: {}".format(proc.returncode))
                error("Command used: {}".format(command))
                error("Trace:\n{}".format(output))
                should_exit = proc.returncode
    except KeyboardInterrupt:
        raise
    except:
        error("Unable to run given executable, does it exist?")
        error("executable: {}".format(command))
        sys.exit(-1)

    if (should_exit != None):
        sys.exit(should_exit)




# function timing
def time_func(function, *args):
    start = time.time()
    ret = function(*args)
    end = time.time()
    return (end-start, ret)




# nicer file parsing for args
class IanArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(IanArgumentParser, self).__init__(*args, **kwargs)

    def convert_arg_line_to_args(self, line):
        try:
            for arg in shlex.split(line):
                if not arg.strip():
                    continue
                if arg[0] == '#':
                    break
                yield arg
        except:
            error("Unable to parse argument string")
            error("given string: {}".format(line))
            sys.exit(-1)
