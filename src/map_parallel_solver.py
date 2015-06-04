import gelpia_utils as GU
import ian_utils as IU

import multiprocessing as MP
import multiprocessing.pool as MPP
import line_profiler as LP
import queue as Q

x_tol = None
f_tol = None
func = None

class Worker(object):
    def __init__(self, _best_low, _best_high):
        self.best_low = _best_low
        self.best_high = _best_high

    def __call__(self, x):
        #IU.log(4, "Working on: {}".format(x))
        # Calculate f(x) and widths of the input and output
        x_width = x.width()
        f_of_x = func(x)
        f_of_x_width = f_of_x.width()

        # Cut off search paths which cannot lead to better answers.
        # Either f(x) has an upper value which is too low, or the intervals are
        # beyond reqested tolerances
        if (f_of_x.upper() < self.best_low or
            x_width < x_tol or
            f_of_x_width < f_tol):
            # Check to see if we have hit the second case and need to update
            # our best answer
            if (self.best_high < f_of_x.upper()):
                return (None, (f_of_x.upper(), x), None)
            return (None, None, None)

        # If we cannot rule out this search path, then split and put the new
        # work onto the queue
        box_list = x.split()
        new_low = None
        for box in box_list:
            estimate = func(box.midpoint())
            # See if we can update our water mark for ruling out search paths
            if (self.best_low < estimate.upper()):
                new_low = estimate.upper()
                
        return (new_low, None, list(box_list))

def first(t): return t[0]
def second(t): return t[1]
def third(t): return t[2]


def solve(X_0, _x_tol, _f_tol, _func, procs, profiler):

    global x_tol
    global f_tol
    global func
    global best_low
    global best_high
    x_tol = _x_tol
    f_tol = _f_tol
    func = _func

    if (profiler):
        profiler.add_function(globopt_worker)

    pool = MPP.Pool(procs)

    boxes = [X_0]
    best_low = GU.large_float("-inf")
    best_high = GU.large_float("-inf")
    best_high_input = X_0
    while (len(boxes) > 0):
        tuples = list(pool.map(Worker(best_low, best_high), boxes))
        lows = [low for low in map(first, tuples) if low]
        highs = [high for high in map(second, tuples) if high]
        work = [w for w in map(third, tuples) if w]
        work = [item for sublist in work for item in sublist]

        if (len(lows) > 0):
            best_low = max(lows)
        if (len(highs) > 0):
            best_high, best_high_input = max(highs, key=lambda t:t[0])
        boxes = work

    return (best_high, best_high_input)
