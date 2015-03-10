#!/usr/bin/env python3

import large_float as lf

a = lf.large_float("10")
b = lf.large_float("20")

assert(a < b)

c = lf.large_float("10")

assert(a == c)
