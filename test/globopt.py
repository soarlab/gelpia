#!/usr/bin/env python3

import large_float as LF
import interval as I
import box as B
import function as F

import queue as Q

def globopt(X_0, x_tol, f_tol, func):
    local_queue = Q.Queue()
    local_queue.put(X_0)

    f_best_low = LF.large_float("-inf")
    f_best_high = LF.large_float("-inf")

    while local_queue.not_empty:
        X = local_queue.get()

        f = func(X)
        w = X.width()
        fw = f.width()

        if (f.upper() < f_best_low
            or w < x_tol
            or fw < f_tol):
            if (f_best_high < f.upper()):
                f_best_high = f.upper()
        else:
            X12 = X.split()
            
            X1 = B.first(X12)
            e = func(X1.midpoint())
            if (f_best_low < e.upper()):
                f_best_low = e.upper()
            local_queue.put(X1)
                
            X2 = B.second(X12)
            e = func(X2.midpoint())
            if (f_best_low < e.upper()):
                f_best_low = e.upper()
            local_queue.put(X2)

    return f_best_high

if __name__ == "__main__":
    X_0 = B.box()
    for i in range(6):
        X_0.append("-100.0", "100.0")


    f_tol = LF.large_float(".0000001")
    x_tol = LF.large_float(".0000001")

    func = F.function

    answer = globopt(X_0, x_tol, f_tol, func)

    print("answer found: {}".format(anser.to_string()))
