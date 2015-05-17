import gelpia_utils as GU

import multiprocessing as MP
from time import sleep


def globopt_worker(my_id,
                   global_queue, 
                   f_best_low, 
                   f_best_high, 
                   do_work):
    while do_work.value:
        try:
            X = global_queue.get(timeout=1)
        except:
            continue

        fx = func(X)
        w = X.width()
        fw = fx.width()
        
        if (fx.upper() < f_best_low
            or w < x_tol
            or fw < f_tol):
            if (f_best_high < f.upper()):
                f_best_high = f.upper()
        else:
            box_list = X.split()
            
            for b in box_list:
                e = func(b.midpoint())
                if(e.upper() > f_best):
                    f_best_low = e.upper()
                global_queue.put(b)
        global_queue.task_done()



def solve(X_0, x_tol, f_tol, func, procs):
    global_queue = MP.JoinableQueue()
    global_queue.put(X_0)

    thnig =     global_queue.get(X_0)
    return 0
    f_best_low = GU.large_float("-inf");
    f_best_high = GU.large_float("-inf");
    
    do_work = MP.Value('b', True)

    process_list = [MP.Process(target=globopt_worker,
                               args=(i, global_queue, 
                                     f_best_low, f_best_high, 
                                     do_work))
                    for i in range(procs)]
    
    for proc in process_list:
        proc.start()

    global_queue.join()
    do_work.value = False

    for proc in process_list:
        proc.join()
    
    
    return f_best
