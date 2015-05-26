import gelpia_utils as GU

import queue as Q

def solve(X_0, x_tol, f_tol, func, procs_ignore, profile):
    local_queue = Q.Queue()
    local_queue.put(X_0)

    f_best_low = GU.large_float("-inf")
    f_best_high = GU.large_float("-inf")

    while not local_queue.empty():
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
            box_list = X.split()
            
            for b in box_list:
                e = func(b.midpoint())
                if (f_best_low < e.upper()):
                    f_best_low = e.upper()
                local_queue.put(b)
                
    return f_best_high
