import gelpia_utils as GU
import ian_utils as IU

import multiprocessing as MP
import line_profiler as LP
import queue as Q
import random as R

colors = [IU.red, IU.green, IU.yellow, IU.blue, IU.magenta, IU.cyan]
def worker_log(level, my_id, message):
    colorize = colors[my_id % len(colors)]
    IU.log(level, colorize("Worker {} - ".format(my_id)) + message)

def globopt_subworker(X_0, x_tol, f_tol, func, update_queue, update_flag, 
                      best_high, best_low, my_id):
    """ Per process prioritized serial branch and bound solver """
    local_queue = Q.PriorityQueue()
    # Since the priority queue needs completely orderable objects we use a
    # monotonic value to decide "ties" in the priority value
    priority_fix = 0
    local_queue.put((0, priority_fix, X_0))

    best_high_input = X_0

    worker_log(3, my_id, "Starting work on interval: {}".format(X_0))
    while (not local_queue.empty()):
        # Attempt to update best_high from other solvers
        if (update_flag.value):
            update_flag.value = False
            temp = update_queue.get()
            # We are only interested in the latest value, ignore others
            while (not update_queue.empty()):
                temp = update_queue.get()
            # Once we have the newest see if we can update
            if (temp > best_low):
                worker_log(3, my_id, "Updated best_low to: {}".format(temp))
                best_low = temp

        # Calculate f(x) and widths of the input and output
        x = local_queue.get()[2]
        x_width = x.width()
        f_of_x = func(x)
        f_of_x_width = f_of_x.width()

        # Cut off search paths which cannot lead to better answers.
        # Either f(x) has an upper value which is too low, or the intervals are
        # beyond reqested tolerances
        if (f_of_x.upper() < best_low or
            x_width < x_tol or
            f_of_x_width < f_tol):
            # Check to see if we have hit the second case and need to update
            # our best answer
            if (best_high < f_of_x.upper()):
                best_high = f_of_x.upper()
                best_high_input = x
            continue

        # If we cannot rule out this search path, then split and put the new
        # work onto the queue
        box_list = x.split()
        for box in box_list:
            estimate = func(box.midpoint())
            # See if we can update our water mark for ruling out search paths
            if (best_low < estimate.upper()):
                best_low = estimate.upper()
            # prioritize the intervals with largest estimates
            priority_fix += 1
            local_queue.put((-estimate.upper(), priority_fix, box))

    worker_log(3, my_id, "Found possible answer: {}".format(best_high))
    return (best_low, best_high, best_high_input)




def globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_queue, update_flag,
                   new_work_queue, my_id):
    """ Per process work consumer """
    best_low = GU.large_float("-inf")
    best_high = GU.large_float("-inf")
    while X_0:
        tup = globopt_subworker(X_0, x_tol, f_tol, func, update_queue,
                                update_flag, best_low, best_high, my_id)
        best_low, best_high, best_high_input = tup
        out_queue.put((my_id, best_low, best_high, best_high_input))
        X_0 = new_work_queue.get()

        


STDOUT_LOCK = MP.Lock()
def globopt_worker_profiling_wrap(X_0, x_tol, f_tol, func, out_queue,
                                  update_queue, update_flag, new_work_queue, 
                                  my_id):
    """ Wraps the worker with a profiler """
    # Each worker has its own profiler
    my_profiler = LP.LineProfiler(globopt_worker, globopt_subworker)
    my_profiler.enable()

    # Use a try statement so that profiling is printed on a control-C
    try:
        globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_queue, 
                       update_flag, new_work_queue, my_id)
    finally:
        my_profiler.disable()
        # Avoid interleaving output
        STDOUT_LOCK.acquire()
        my_profiler.print_stats()
        STDOUT_LOCK.release()

        

def solve(X_0, x_tol, f_tol, func, procs, profiler):
    """ Higher utilization version of the split parallel solver """
    # split input into many pieces
    boxes = Q.Queue()
    boxes.put(X_0)
    piece_count = max(X_0.size()*2, procs*2)
    for i in range(piece_count):
        new_box = boxes.get()
        box_list = new_box.split()
        for box in box_list:
            boxes.put(box)

    # randomize pieces
    pieces = list()
    for i in range(piece_count):
        pieces.append(boxes.get())
    R.seed(42)
    R.shuffle(pieces)
    for p in pieces:
        boxes.put(p)
    
    # All answers found by solvers are put in here
    answer_queue = MP.Queue()

    # Updates to best_high are sent through this list
    update_queue_list = [MP.Queue() for i in range(procs)]
    update_flag_list = [MP.Value('b', False) for i in range(procs)]

    # Work is fed to workser throught these queues
    new_work_queues = [MP.Queue() for i in range(procs)]

    # Should the performance profiler be used?
    worker = globopt_worker_profiling_wrap if profiler else globopt_worker

        
    process_list = [MP.Process(target=worker,
                                       args=(boxes.get(), x_tol, f_tol, func, 
                                             answer_queue,
                                             update_queue_list[i],
                                             update_flag_list[i],
                                             new_work_queues[i], i))
                                             
                    for i in range(procs)]

    for proc in process_list:
        proc.start()

    # Get answers from finished solvers, send updates if needed
    best_low = GU.large_float("-inf")
    best_high = GU.large_float("-inf")
    best_input = X_0
    done_count = 0
    while (done_count < procs):
        tup =answer_queue.get()
        proc_num, next_best_low, next_best_high, next_best_input = tup

        # Update anser
        if (next_best_high > best_high):
            best_high = next_best_high
            best_high_input = next_best_input

        # Update water mark
        if (next_best_low > best_low):
            best_low = next_best_low
            IU.log(3, "Sending update to workers: {}".format(best_low))
            for i in range(procs):
                if (i != proc_num):
                    update_queue_list[i].put(best_low)
                    update_flag_list[i].value = True

        if (not boxes.empty()):
            # Give the finished worker more work
            new_work_queues[proc_num].put(boxes.get())
        else:
            # Give the finished worker a poison pill
            IU.log(3, "Killing Process {}".format(proc_num))
            new_work_queues[proc_num].put(None)
            done_count += 1

    # Wait for all workers to exit
    for proc in process_list:
        proc.join()

    return (best_high, best_high_input)
