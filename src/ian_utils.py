#!/usr/bin/env python3
import subprocess as SP
import argparse as AP
import shlex as SHL
import signal as SIG
import sys as SYS
import time as T

# optional color printing
DO_COLOR = True

def use_color_printing():
    global DO_COLOR
    DO_COLOR = True

def use_plain_printing():
    global DO_COLOR
    DO_COLOR = False

def color_text(color_code, text):
    if DO_COLOR:
        return "{}{}{}".format(color_code, text, "\x1b[0m")
    else:
        return text

def black(text):
    return color_text("\x1b[30m", text)

def red(text):
    return color_text("\x1b[31m", text)

def green(text):
    return color_text("\x1b[32m", text)

def yellow(text):
    return color_text("\x1b[33m", text)

def blue(text):
    return color_text("\x1b[34m", text)

def magenta(text):
    return color_text("\x1b[35m", text)

def cyan(text):
    return color_text("\x1b[36m", text)

def white(text):
    return color_text("\x1b[37m", text)




# logging to stdout
LOG_LEVEL = 0

def set_log_level(level):
    global LOG_LEVEL
    LOG_LEVEL = level

def get_log_level():
    return LOG_LEVEL

def log(level, *objs):
    if (level <= LOG_LEVEL):
        print(*objs)




# printing to stderr
def error(*objs):
    print(red("ERROR:"), *objs, file=SYS.stderr)

def warning(*objs):
    print(yellow("WARNING:"), *objs, file=SYS.stderr)



# Formatted printing
def box_text(line_list, width,
             top_left="+", top="-", top_right="+",
             left="|", right="|",
             bottom_left="+", bottom="-", bottom_right="+"):
    box = list()
    width_for_top = width - (len(top_left) + len(top_right))
    box.append("{}{}{}".format(top_left,
                               top * (width_for_top // len(top)),
                               top_right))

    width_for_middle = width - (len(left) + len(right))
    format_string = "{}{:"+str(width_for_middle)+"}{}"
    box.extend([format_string.format(left, line, right) for line in line_list])

    width_for_bottom = width - (len(bottom_left) + len(bottom_right))
    box.append("{}{}{}".format(bottom_left,
                               bottom * (width_for_bottom // len(bottom)),
                               bottom_right))

    return box

def comment_block(line_list, width):
    return box_text(line_list, width,
                   "/*","*","*",
                   " * ", "",
                   " *", "*", "*/")



# popen wrappers
def run(cmd, args_list, error_string):
    command = cmd+" "+" ".join(args_list)
    with SP.Popen(command,
                  stdout=SP.PIPE, stderr=SP.STDOUT,shell=True) as proc:
        output = proc.stdout.read().decode("utf-8")
        proc.wait()

        if proc.returncode != 0:
            error(error_string)
            error("Non-zero return code: {}".format(proc.returncode))
            error("Command used: {}".format(command))
            error("Trace:\n{}".format(output))
            SYS.exit(proc.returncode)

    return output



# catching sigint
def sigint_handler(signal, frame):
    print("", file=SYS.stderr)
    warning("Program exiting without cleanup")
    SYS.exit(0)

SIG.signal(SIG.SIGINT, sigint_handler)




# function timing
def time_func(function, *args):
    start = T.time()
    ret = function(*args)
    end = T.time()
    return (end-start, ret)



# nicer file paring for args
class IanArgumentParser(AP.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(IanArgumentParser, self).__init__(*args, **kwargs)

    def convert_arg_line_to_args(self, line):
        try:
            for arg in SHL.split(line):
                if not arg.strip():
                    continue
                if arg[0] == '#':
                    break
                yield arg
        except:
            error("Unable to parse argument string")
            error("given string: {}".format(line))
            SYS.exit(-1)
