import gelpia_utils as GU

import multiprocessing as MP
import line_profiler as LP
from time import sleep

        
def globopt_worker(x_tol, f_tol, func, global_queue, ns):
    while True:
        X = global_queue.get()

        try:
            X == None
            return
        except:
            pass
        
        f = func(X)
        w = X.width()
        fw = f.width()
        
        if (f.upper() < ns.f_best_low
            or w < x_tol
            or fw < f_tol):
            if (ns.f_best_high < f.upper()):
                ns.f_best_high = f.upper()
        else:
            box_list = X.split()
            
            for b in box_list:
                e = func(b.midpoint())
                if(ns.f_best_low < e.upper()):
                    ns.f_best_low = e.upper()
                global_queue.put(b)
        global_queue.task_done()




def globopt_worker_wrap(x_tol, f_tol, func, global_queue, ns):
    my_profiler = LP.LineProfiler(globopt_worker)
    my_profiler.enable()
    try:
        globopt_worker(x_tol, f_tol, func, global_queue, ns)
    finally:
        my_profiler.disable()
        my_profiler.print_stats()



    
def solve(X_0, x_tol, f_tol, func, procs, profiler):
    global_queue = MP.JoinableQueue()
    global_queue.put(X_0)
    
    mgr = MP.Manager()
    ns = mgr.Namespace()
    ns.f_best_low = GU.large_float("-inf")
    ns.f_best_high = GU.large_float("-inf")
    ns.x_tol = x_tol
    ns.f_tol = f_tol

    worker = globopt_worker
    if profiler:
        worker = global_worker_wrap
        
    process_list = [MP.Process(target=worker,
                               args=(x_tol, f_tol, func, global_queue, ns))
                    for i in range(procs)]

    for proc in process_list:
        proc.start()

    global_queue.join()

    for proc in process_list:
        global_queue.put(None)

    for proc in process_list:
        proc.join()
    
    return ns.f_best_high
