#!/usr/bin/env python3
PROCS = 2

import large_float as LF
import interval as I
import function as F

import multiprocessing as mp
from time import sleep

#@profile
def globopt_worker(my_id, working_list, global_queue, f_best, f_best_lock):
    while True:
        working_list[my_id] = 0
        try:
            X = global_queue.get(block=True, timeout=3)
        except:
            continue

        working_list[my_id] = 1
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
            global_queue.put((e.upper().neg(), X1))

            X2 = X.second(index)
            e = func(X2.midpoint())
            if(e.upper() > f_best):
                f_best = e.upper()
            global_queue.put((e.upper().neg(), X2))
        



#@profile
def globopt(X_0, x_tol, f_tol, func):
    global_queue = mp.Queue()
    global_queue.put(X_0)
    
    f_best = LF.large_float("-inf");
    f_best_lock = mp.Lock()

    working_list = [1 for i in range(PROCS)]
    
    process_list = [mp.Process(target=globopt_worker,
                               args=(i, working_list, global_queue, f_best, f_best_lock,))
                    for i in range(PROCS)]
    
    for proc in process_list:
        proc.start()

    sleep(1)

    while (sum(working_list) > 0):
        sleep(1)
    
    return f_best

            


if __name__ == "__main__":
    X_0 = F.box()
    for i in range(6):
        X_0.append("0", ".1")


    f_tol = LF.large_float(".01")
    x_tol = LF.large_float(".01")

    func = F.function

    answer = globopt(X_0, x_tol, f_tol, func)

    print("answer found: {}".format(answer))
