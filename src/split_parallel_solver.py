import gelpia_utils as GU

import multiprocessing as MP
import queue as Q
import ctypes as CT
from time import sleep

def globopt_worker(X_0, x_tol, f_tol, func, out_queue):
    local_queue = Q.PriorityQueue()
    local_queue.put((0, 0, X_0))
    priority_fix = 0
    f_best = GU.large_float("-inf");
    
    while not local_queue.empty():
        ignore_0, ignore_1, X = local_queue.get()

        fx = func(X)
        w = X.width()
        fw = fx.width()
        
        if (fx.upper() < f_best or
            w < x_tol or
            fw < f_tol):
            continue
        else:
            box_list = X.split()
            
            for b in box_list:
                e = func(b.midpoint())
                if(e.upper() > f_best):
                    f_best = e.upper()
                priority_fix += 1
                local_queue.put((-e.upper(), priority_fix, b))

    out_queue.put(f_best)




def solve(X_0, x_tol, f_tol, func, procs):
    boxes = Q.Queue()
    boxes.put(X_0)
    for i in range(procs-1):
        new_box = boxes.get()
        box_list = new_box.split()
        for b in box_list:
            boxes.put(b)
    assert(boxes.qsize() == procs)

    answer_queue= MP.Queue()

    process_list = list()
    for i in range(procs):
        process_list.append(MP.Process(target=globopt_worker,
                                       args=(boxes.get(), x_tol, f_tol, func, 
                                             answer_queue)))
    assert(boxes.empty())

    for proc in process_list:
        proc.start()

    for proc in process_list:
        proc.join()
        
    best = answer_queue.get()
    while not answer_queue.empty():
        ans = answer_queue.get()
        if (ans > best):
            best = ans
    
    
    return best
