import gelpia_utils as GU
import ian_utils as IU

import multiprocessing as MP
import line_profiler as LP
import queue as Q
import ctypes as CT
from time import sleep

STDOUT_LOCK = MP.Lock()

def globopt_subworker(X_0, x_tol, f_tol, func, update_pipe):
    local_queue = Q.PriorityQueue()
    local_queue.put((0, 0, X_0))
    priority_fix = 0
    f_best = GU.large_float("-inf");

    IU.log(3, "Starting work on interval: {}".format(X_0))
    while not local_queue.empty():
        try:
            temp = update_pipe.get_nowait()
            IU.log(3, "Might update f_best: (?> {} {})".format(temp, f_best))
            if (temp > f_best):
                IU.log(3, "Updated f_best to: {}".format(temp))
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
    IU.log(3, "Found possible answer: {}".format(f_best))
    return f_best


def globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_pipe,
                   new_work_queue, my_id):
    while X_0:
        local_best = globopt_subworker(X_0, x_tol, f_tol, func, update_pipe)
        out_queue.put((my_id, local_best))
        X_0 = new_work_queue.get()

        



def globopt_worker_wrap(X_0, x_tol, f_tol, func, out_queue, update_pipe,
                        new_work_queue, my_id):
    my_profiler = LP.LineProfiler(globopt_worker, globopt_subworker)
    my_profiler.enable()
    try:
        globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_pipe,
                       new_work_queue, my_id)
    finally:
        my_profiler.disable()
        STDOUT_LOCK.acquire()
        my_profiler.print_stats()
        STDOUT_LOCK.release()

        

def solve(X_0, x_tol, f_tol, func, procs, profiler):
    boxes = Q.Queue()
    boxes.put(X_0)
    for i in range(procs*4):
        new_box = boxes.get()
        box_list = new_box.split()
        for b in box_list:
            boxes.put(b)

    answer_queue = MP.Queue()

    pipe_list = [MP.Queue() for i in range(procs)]
    new_work_queues = [MP.Queue() for i in range(procs)]
    
    worker = globopt_worker
    if profiler:
        worker = globopt_worker_wrap
        
    process_list = list()        
    for i in range(procs):
        process_list.append(MP.Process(target=worker,
                                       args=(boxes.get(), x_tol, f_tol, func, 
                                             answer_queue, pipe_list[i],
                                             new_work_queues[i], i)))

    for proc in process_list:
        proc.start()

    best = GU.large_float("-inf");
    done_count = 0
    while done_count < procs:
        proc_num, next_best = answer_queue.get()
        if next_best > best:
            best = next_best
            for pipe in pipe_list:
                IU.log(3, "Sending update to workers: {}".format(best))
                try:
                    pipe.put(best)
                except:
                    pass
        if boxes.empty():
            IU.log(3, "Killing Process {}".format(proc_num))
            new_work_queues[proc_num].put(None)
            done_count += 1
        else:
            new_work_queues[proc_num].put(boxes.get())

    for proc in process_list:
        proc.join()

    return best
