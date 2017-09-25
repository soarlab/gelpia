#! /usr/bin/env python3
""" Runs gelpia in parallel in minimization mode and maximization mode for """
""" FPTaylor's min_max_expr solver.                                        """

import multiprocessing
import multiprocessing.pool as pool
import subprocess
import sys
import os
import os.path as path
import shlex

full_dir = path.abspath(path.dirname(sys.argv[0])) # Directory for this file
base_dir = path.split(full_dir)[0] # One directory up
bin_dir = path.join(base_dir, "bin")
gelpia_exe = bin_dir+"/gelpia"

MAX = None
MAX_l = None
MIN = None
MIN_u = None

def get_max(tup):
  out, err = tup
  global MAX
  global MAX_l
  try:
    s = out.split('\n')
    MAX_l = s[0]
    MAX = s[1]
  except:
    pass
    print("MAX FAILED:", out, '\n', err, file=sys.stderr)

def get_min(tup):
  out, err = tup
  global MIN
  global MIN_u
  try:
    s = out.split('\n')
    MIN = s[0]
    MIN_u = s[1]
  except:
    pass
    print("MIN FAILED:", out, '\n', err, file=sys.stderr)

def run_command(cmd):
  cmd = shlex.split(' '.join(cmd))
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  out, err  = p.communicate()
  out = out.decode('utf-8')
  err = err.decode('utf-8')
  return out, err

def main():
  p = multiprocessing.pool.ThreadPool(processes=2)
  cmd1 = [gelpia_exe] + sys.argv[1:]
  cmd2 = [gelpia_exe, "--dreal"] + sys.argv[1:]
  r1 = p.apply_async(run_command,
                     args=(cmd1[:],),
                     callback=get_max)

  r2 = p.apply_async(run_command,
                     args=(cmd2[:],),
                     callback=get_min)

  r1.wait()
  r2.wait()
  p.close()
  p.join()

  if MAX is not None:
    print("Maximum: {}\nMaximum_l: {}".format(MAX, MAX_l))
  else:
    print("Maximum: inf\nMaximum_l: inf")
  if MIN is not None:
    print("Minimum: {}\nMinimum_u: {}".format(MIN, MIN_u))
  else:
    print("Minimum: -inf\nMinimum_u: -inf")

if __name__ == '__main__':
    main()
