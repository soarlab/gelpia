

import subprocess
import argparse
import shlex
import sys
import time
import threading
import queue

import color_printing as color
import gelpia_logging as logging
logger = logging.make_module_logger(color.cyan("ian_utils"))


class AsyncReader(threading.Thread):
    def __init__(self, fil, q):
        threading.Thread.__init__(self)
        self.q = q
        self.fil = fil

    def run(self):
        output = "empty"
        while output != "":
            output = self.fil.readline()
            self.q.put(output)


def run_async(cmd, args_list, timeout, error_string="An Error has occured",
              expected_return=0):
    command = [cmd] + args_list
    should_exit = None
    term_time = time.time() + timeout
    try:
        with subprocess.Popen(command,
                              bufsize=1,
                              universal_newlines=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:

            # Asynchronously collect messages
            stdout_q = queue.Queue()
            stdout_r = AsyncReader(proc.stdout, stdout_q)
            stdout_r.start()
            output = []

            while proc.poll() is None:
                if not stdout_q.empty():
                    line = stdout_q.get()
                    output.append(line)
                    yield line

                # Kill proc if timeout exceeded
                if term_time is not None:
                    if timeout != 0 and time.time() > term_time:
                        print("Killed by timeout")
                        proc.kill()
                #time.sleep(0.1)

            # Clear remaining buffered messages
            while stdout_r.is_alive() or not stdout_q.empty():
                if not stdout_q.empty():
                    yield stdout_q.get()

            proc.wait()
            if (expected_return is not None) and (proc.returncode not in
                                                  (expected_return, -9)):
                logging.error(error_string)
                logging.error("Return code: {}".format(proc.returncode))
                logging.error("Command used: {}".format(command))
                logging.error("Trace:\n{}".format("\n".join(output)))
                should_exit = proc.returncode
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logging.error("Unable to run given executable, does it exist?")
        logging.error("executable: {}".format(command))
        logging.error("Python exception: {}", e)
        try:
            logging.error("Trace:\n{}".format("\n".join(output)))
        except:
            pass
        sys.exit(-1)

    if (should_exit is not None):
        sys.exit(should_exit)
