#! /usr/bin/env python3
""" Runs gelpia in parallel in minimization mode and maximization mode for """
""" FPTaylor's min_max_expr solver.                                        """

import multiprocessing
import multiprocessing.pool as pool
import re
import subprocess
import sys
import os
import os.path as path
import shlex

full_dir = path.abspath(path.dirname(__file__)) # Directory for this file
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
    MAX = re.search("Maximum: ([^\n]*)", out).group(1)
    MAX_l = re.search("Maximum_l: ([^\n]*)", out).group(1)
  except:
    print("MAX FAILED:\nout:\n{}\n\nerr:\n{}\n".format(out, err))

def get_min(tup):
  out, err = tup
  global MIN
  global MIN_u
  try:
    MIN = re.search("Minimum: ([^\n]*)", out).group(1)
    MIN_u = re.search("Minimum_u: ([^\n]*)", out).group(1)
  except:
    print("MIN FAILED:\nout:\n{}\n\nerr:\n{}\n".format(out, err))

def run_command(cmd):
  cmd = shlex.split(' '.join(cmd))
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  out, err  = p.communicate()
  out = out.decode('utf-8')
  err = err.decode('utf-8')
  return out, err

def main(argv):
  p = multiprocessing.pool.ThreadPool(processes=2)
  cmd1 = [gelpia_exe] + argv[1:]
  cmd2 = [gelpia_exe, "--dreal"] + argv[1:]
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
    main(sys.argv)
