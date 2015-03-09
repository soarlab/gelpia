#!/usr/bin/env python3
# MUST be run from the bin dir

import optimizer_helpers as oh
import queue

x_tol = float("0."+"0"*323+"1")
f_tol = float("0."+"0"*323+"1")
max_iter = float("inf")

def main():
    Q = queue.Queue()
    Q.put(oh.new_box())
    
    f_best_low = -float("inf")
    f_best_high = -float("inf")

    iter_count = 0

    while not Q.empty():
        X = Q.get()

        f = oh.func(X)
        w = oh.width(X)
        fw = oh.upper(f) - oh.lower(f) 

        if (oh.upper(f) < f_best_low
            or w <= x_tol
            or fw <= f_tol
            or iter_count > max_iter):
            f_best_high = max(f_best_high, oh.upper(f));
        else:
            iter_count += 1
            X_12 = oh.split_box(X)

            X_1 = oh.left(X_12)
            e = oh.midpoint(X_1)
            f_best_low = max(oh.point(e), f_best_low)
            Q.put(X_1)

            X_2 = oh.right(X_12)
            e = oh.midpoint(X_2)
            f_best_low = max(oh.point(e), f_best_low)
            Q.put(X_2)

    return f_best_high


if __name__ == "__main__":
    print("\n\nanswer found: {}\n".format(main()))
