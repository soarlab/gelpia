import gelpia_utils as GU
import ian_utils as IU

import multiprocessing as MP
import line_profiler as LP
import queue as Q

def globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_queue, my_id):
    """ Per process solver using no shared state """
    local_queue = Q.PriorityQueue()
    # Since the priority queue needs completely orderable objects we use a
    # monotonic value to decide "ties" in the priority value
    priority_fix = 0
    local_queue.put((0, priority_fix, X_0))

    best_low = GU.large_float("-inf")
    best_high = GU.large_float("-inf")
    best_high_input = X_0

    IU.log(3, "Worker {} - Starting work on interval: {}".format(my_id, X_0))
    while (not local_queue.empty()):
        # Attempt to update best_high from other solvers
        if (not update_queue.empty()):
            temp = update_queue.get()
            # We are only interested in the latest value, ignore others
            while (not update_queue.empty()):
                temp = update_queue.get()
            # Once we have the newest see if we can update
            if (temp > best_high):
                IU.log(3, "Worker {} - Updated best_high to: {}".format(my_id,
                                                                        temp))
                best_high = temp
            else:
                IU.log(3, "Worker {} - Not updated best_high: {}".format(my_id,
                                                                      best_high))

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

    IU.log(3, "Found possible answer: {}".format(best_high))
    out_queue.put((best_high, best_high_input))



STDOUT_LOCK = MP.Lock()
def globopt_worker_profiling_wrap(X_0, x_tol, f_tol, func, out_queue, update_queue,
                                 my_id):
    """ Wraps the worker with a profiler """
    # Each worker has its own profiler
    my_profiler = LP.LineProfiler(globopt_worker)
    my_profiler.enable()

    # Use a try statement so that profiling is printed on a control-C
    try:
        globopt_worker(X_0, x_tol, f_tol, func, out_queue, update_queue, my_id)
    finally:
        my_profiler.disable()
        # Avoid interleaving output
        STDOUT_LOCK.acquire()
        my_profiler.print_stats()
        STDOUT_LOCK.release()




def solve(X_0, x_tol, f_tol, func, procs, profiler):
    """ Parallel branch and bound solver with no shared state """
    # split input into procs pieces
    boxes = Q.Queue()
    boxes.put(X_0)
    for i in range(procs-1):
        new_box = boxes.get()
        box_list = new_box.split()
        for box in box_list:
            boxes.put(box)

    # All answers found by solvers are put in here
    answer_queue = MP.Queue()

    # Updates to best_high are sent through this list
    update_queue_list = [MP.Queue() for i in range(procs)]

    # Should the performance profiler be used?
    worker = globopt_worker_profiling_wrap if profiler else globopt_worker

    process_list = [MP.Process(target=worker,
                               args=(boxes.get(), x_tol, f_tol, func,
                                     answer_queue, update_queue_list[i], i))
                    for i in range(procs)]

    for proc in process_list:
        proc.start()

    # Get answers from finished solvers, send updates if needed
    best = GU.large_float("-inf")
    best_input = X_0
    for i in range(procs):
        next_best, next_best_input = answer_queue.get()
        if (next_best > best):
            best = next_best
            best_input = next_best_input
            IU.log(3, "Sending update to workers: {}".format(best))
            for q in update_queue_list:
                q.put(best)

    # Wait for all workers to exit
    for proc in process_list:
        proc.join()

    return (best, best_input)
