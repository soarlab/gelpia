import gelpia_utils as GU
import ian_utils as IU

import multiprocessing as MP
import line_profiler as LP
import queue as Q
import ctypes as CT
from time import sleep

STDOUT_LOCK = MP.Lock()

def globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_pipe):
    local_queue = Q.PriorityQueue()
    local_queue.put((0, 0, X_0))
    priority_fix = 0
    f_best = GU.large_float("-inf");
    
    while not local_queue.empty():
        try:
            temp = update_pipe.get_nowait()
            IU.log(3, "Might update f_best: (?> {} {})".format(temp, f_best))
            if (temp > f_best):
                IU.log(3, print("Updated f_best to: {}".format(temp)))
                f_best = temp
            else:
                IU.log(3, "Not updated f_best: {}".format(f_best))
        except Q.Empty:
            pass
        
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
    print("Found possible answer: {}".format(f_best))
    out_queue.put(f_best)




def globopt_worker_wrap(X_0, x_tol, f_tol, func, out_queue, update_pipe):
    my_profiler = LP.LineProfiler(globopt_worker)
    my_profiler.enable()
    try:
        globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_pipe)
    finally:
        my_profiler.disable()
        STDOUT_LOCK.acquire()
        my_profiler.print_stats()
        STDOUT_LOCK.release()

        

def solve(X_0, x_tol, f_tol, func, procs, profiler):
    boxes = Q.Queue()
    boxes.put(X_0)
    for i in range(procs-1):
        new_box = boxes.get()
        box_list = new_box.split()
        for b in box_list:
            boxes.put(b)
    assert(boxes.qsize() == procs)

    answer_queue = MP.Queue()

    pipe_list = [MP.Queue() for i in range(procs)]

    worker = globopt_worker
    if profiler:
        worker = globopt_worker_wrap
        
    process_list = list()        
    for i in range(procs):
        process_list.append(MP.Process(target=worker,
                                       args=(boxes.get(), x_tol, f_tol, func, 
                                             answer_queue, pipe_list[i])))
            
    assert(boxes.empty())

    for proc in process_list:
        proc.start()

    best = GU.large_float("-inf");
    for i in range(procs):
        next_best = answer_queue.get()
        if next_best > best:
            best = next_best
            for pipe in pipe_list:
                IU.log(3, "Sending update to workers: {}".format(best))
                try:
                    pipe.put_nowait(best)
                except:
                    pass

    for proc in process_list:
        proc.join()

    return best
