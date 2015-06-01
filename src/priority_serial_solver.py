import gelpia_utils as GU

import queue as Q

def solve(X_0, x_tol, f_tol, func, procs_ignore, profiler):
    local_queue = Q.PriorityQueue()
    local_queue.put((0, 0, X_0))
    priority_fix = 0
    f_best_low = GU.large_float("-inf")
    f_best_high = GU.large_float("-inf")
    
    while not local_queue.empty():
        ignore_0, ignore_1, X = local_queue.get()
        fx = func(X)
        w = X.width()
        fw = fx.width()
        if (fx.upper() < f_best_low or
            w < x_tol or
            fw < f_tol):
            if f_best_high < fx.upper():
                f_best_high = fx.upper()
        else:
            box_list = X.split()
            
            for b in box_list:
                e = func(b.midpoint())
                if(e.upper() > f_best_low):
                    f_best_low = e.upper()
                priority_fix += 1
                local_queue.put((-e.upper(), priority_fix, b))

    return f_best_high
