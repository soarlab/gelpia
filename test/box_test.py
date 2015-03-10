#!/usr/bin/env python3
import box as B


a = B.box()
for i in range(10):
    a.append("-10", "10")
    assert(a.size() == i+1)

b = B.box(a)

assert(a.size() == 10)
assert(b.size() == a.size())
