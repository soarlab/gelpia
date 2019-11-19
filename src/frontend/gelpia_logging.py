

import color_printing as color

import sys




NONE    = 0
LOW     = 10
MEDIUM  = 20
HIGH    = 30

LEVELS = {
    "none"   : NONE,
    "low"    : LOW,
    "medium" : MEDIUM,
    "high"   : HIGH,
}

LOG_LEVEL = None
LOG_FILE = None




def set_log_level(level):
    global LOG_LEVEL
    LOG_LEVEL = level


def get_log_level():
    return LOG_LEVEL


def set_log_filename(filename):
    global LOG_FILE
    if filename is None:
        LOG_FILE = sys.stdout
    else:
        LOG_FILE = open(filename, "w")


def get_log_file():
    return LOG_FILE


def log(level, module, message, *args):
    if level <= LOG_LEVEL:
        formatted_message = "{}: {}".format(module, message.format(*args))
        if LOG_FILE != sys.stdout:
            formatted_message = color.strip(formatted_message)
        print(formatted_message, file=LOG_FILE)

def make_module_logger(module, level=None):
    if level is None:
        return lambda level, message, *args : log(level, module, message, *args)
    else:
        return lambda message, *args : log(level, module, message, *args)

def error(message, *args):
    formatted_message = "{}: {}".format(color.red("ERROR"),
                                        message.format(*args))
    print(formatted_message, file=sys.stderr)
    if LOG_FILE != sys.stdout:
        print(color.strip(formatted_message), file=LOGFILE)


def warning(message, *args):
    formatted_message = "{}: {}".format(color.yellow("WARNING"),
                                        message.format(*args))
    print(formatted_message, file=sys.stderr)
    if LOG_FILE != sys.stdout:
        print(color.strip(formatted_message), file=LOGFILE)


