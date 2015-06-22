import gelpia_utils as GU

import queue as Q

def solve(X_0, x_tol, f_tol, func, procs_ignore, profile_ignore):
    """ Naive serial branch and bound solver """
    local_queue = Q.Queue()
    local_queue.put(X_0)

    best_low = GU.large_float("-inf")
    best_high = GU.large_float("-inf")
    best_high_input = X_0

    while (not local_queue.empty()):
        # Calculate f(x) and widths of the input and output
        x = local_queue.get()
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
            local_queue.put(box)

    return (best_high, best_high_input)
