#!/usr/bin/env python3

import large_float as LF
import interval as I
import function as F

import queue as Q

def globopt(X_0, x_tol, f_tol, func):
    local_queue = Q.Queue()
    local_queue.put(X_0)
    
    f_best = LF.large_float("-inf");

    count = 0
    
    while not local_queue.empty():
        count += 1

        X = local_queue.get()

        fx = func(X)
        w = X.width()
        fw = fx.width()
        
        if (fx.upper() < f_best or
            w < x_tol or
            fw < f_tol):
            continue
        else:
            index = X.split_index()
            
            X1 = X.first(index)
            e = func(X1.midpoint())
            if(e.upper() > f_best):
                f_best = e.upper()
            local_queue.put(X1)

            X2 = X.second(index)
            e = func(X2.midpoint())
            if(e.upper() > f_best):
                f_best = e.upper()
            local_queue.put(X2)

    return f_best

            


if __name__ == "__main__":
    X_0 = F.box()
    for i in range(6):
        X_0.append("0", ".1")


    f_tol = LF.large_float(".001")
    x_tol = LF.large_float(".001")

    func = F.function

    answer = globopt(X_0, x_tol, f_tol, func)

    print("answer found: {}".format(answer))
