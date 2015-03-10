#!/usr/bin/env python3
import large_float as LF
import interval as I

a = I.interval("10", "20")
l = LF.large_float("10")
u = LF.large_float("20")

assert(a.lower() == l)
assert(a.upper() == u)
