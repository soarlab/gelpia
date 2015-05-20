import gelpia_utils as GU

import multiprocessing as MP
from time import sleep

def globopt_worker(x_tol, f_tol, func, global_queue, ns, do_work):
    while do_work.value:
        try:
            X = global_queue.get(timeout=1)
        except:
            continue

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



def solve(X_0, x_tol, f_tol, func, procs):
    global_queue = MP.JoinableQueue()
    global_queue.put(X_0)
    
    mgr = MP.Manager()
    ns = mgr.Namespace()
    ns.f_best_low = GU.large_float("-inf");
    ns.f_best_high = GU.large_float("-inf");

    do_work = MP.Value('b', True)

    process_list = [MP.Process(target=globopt_worker,
                               args=(x_tol, f_tol, func, global_queue, ns, do_work))
                    for i in range(procs)]
    
    for proc in process_list:
        proc.start()

    global_queue.join()
    do_work.value = False

    for proc in process_list:
        proc.join()
    
    
    return ns.f_best_high
