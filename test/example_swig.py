#!/usr/bin/env python3
# MUST be run from the bin dir

import optimizer_helpers as oh

b = oh.new_box([-1., -2.], [1., 2.], 2)

[b1, b2] = oh.split_box(b)

m = oh.midpoint(b)

w = oh.width(b)
