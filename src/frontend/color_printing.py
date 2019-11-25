

import sys


if sys.stdout.isatty():
    DO_COLOR = True
else:
    DO_COLOR = False


COLOR_CODES = {
    "black":   "\x1b[30m",
    "red":     "\x1b[31m",
    "green":   "\x1b[32m",
    "yellow":  "\x1b[33m",
    "blue":    "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan":    "\x1b[36m",
    "white":   "\x1b[37m",
    "none":    "\x1b[0m",
}


def use_color_printing():
    global DO_COLOR
    DO_COLOR = True


def use_plain_printing():
    global DO_COLOR
    DO_COLOR = False


def color_text(color, text):
    if DO_COLOR:
        color_code = COLOR_CODES[color.lower()]
        none = COLOR_CODES["none"]
        return "{}{}{}".format(color_code, text, none)
    else:
        return text


def strip(text):
    for code in COLOR_CODES.values():
        text = text.replace(code, "")
    return text


def black(text):
    return color_text("black", text)


def red(text):
    return color_text("red", text)


def green(text):
    return color_text("green", text)


def yellow(text):
    return color_text("yellow", text)


def blue(text):
    return color_text("blue", text)


def magenta(text):
    return color_text("magenta", text)


def cyan(text):
    return color_text("cyan", text)


def white(text):
    return color_text("white", text)
