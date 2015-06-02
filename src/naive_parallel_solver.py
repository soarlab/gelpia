import gelpia_utils as GU

import multiprocessing as MP
import line_profiler as LP

def globopt_worker(x_tol, f_tol, func, global_queue, ns):
    """ Per process solver using shared stated """
    while True:
        x = global_queue.get()

        # look for poison pill
        if (not x):
            return

        # Calculate f(x) and widths of the input and output
        x_width = x.width()
        f_of_x = func(x)
        f_of_x_width = f_of_x.width()

        # Cut off search paths which cannot lead to better answers.
        # Either f(x) has an upper value which is too low, or the intervals are
        # beyond reqested tolerances
        if (f_of_x.upper() < ns.best_low or
            x_width < x_tol or
            f_of_x_width < f_tol):
            # Check to see if we have hit the second case and need to update
            # our best answer
            if (ns.best_high < f_of_x.upper()):
                ns.best_high = f_of_x.upper()
                ns.best_high_input = x
            # Indicate that the work has been done
            global_queue.task_done()
            continue

        # If we cannot rule out this search path, then split and put the new
        # work onto the queue
        box_list = x.split()
        for box in box_list:
            estimate = func(box.midpoint())
            # See if we can update our water mark for ruling out search paths
            if(ns.best_low < estimate.upper()):
                ns.best_low = estimate.upper()
            global_queue.put(box)

        # Indicate that the work has been done
        global_queue.task_done()



STDOUT_LOCK = MP.Lock()
def globopt_worker_profiling_wrap(x_tol, f_tol, func, global_queue, ns):
    """ Wraps the worker with a profiler """
    # Each worker has its own profiler
    my_profiler = LP.LineProfiler(globopt_worker)
    my_profiler.enable()

    # Use a try statement so that profiling is printed on a control-C
    try:
        globopt_worker(x_tol, f_tol, func, global_queue, ns)
    finally:
        my_profiler.disable()
        # Avoid interleaving output
        STDOUT_LOCK.acquire()
        my_profiler.print_stats()
        STDOUT_LOCK.release()



def solve(X_0, x_tol, f_tol, func, procs, profiler):
    """ Naive parallel branch and bound solver """
    global_queue = MP.JoinableQueue()
    global_queue.put(X_0)

    # Namespace is used to have shared state
    # Namespaces are very costly
    mgr = MP.Manager()
    ns = mgr.Namespace()
    ns.best_low = GU.large_float("-inf")
    ns.best_high = GU.large_float("-inf")
    ns.best_high_input = X_0

    # Should the performance profiler be used?
    worker = globopt_worker_profiling_wrap if profiler else globopt_worker

    process_list = [MP.Process(target=worker,
                               args=(x_tol, f_tol, func, global_queue, ns))
                    for i in range(procs)]

    for proc in process_list:
        proc.start()

    # Join will finish when all work is done
    global_queue.join()

    # Give all workers a poison pill
    for proc in process_list:
        global_queue.put(None)

    # Wait for all workers to exit
    for proc in process_list:
        proc.join()

    return (ns.best_high, ns.best_high_input)
