#!/usr/bin/env python3

from os import path
from multiprocessing.pool import ThreadPool
import multiprocessing
import os
import signal
import logging
import argparse
from os import path
import subprocess
import re
import glob
import time
import sys

OVERRIDE_FIELDS = ['verifiers', 'memory', 'time-limit', 'skip', 'expect']
APPEND_FIELDS = ['flags']

def bold(text):
  return '\033[1m' + text + '\033[0m'

def red(text, log_file):
  if log_file:
    return text
  else:
    return '\033[0;31m' + text + '\033[0m'

def green(text, log_file):
  if log_file:
    return text
  else:
    return '\033[0;32m' + text + '\033[0m'

def yellow(text, log_file):
  if log_file:
    return text
  else:
    return '\033[0;33m' + text + '\033[0m'

def get_result(output):
  match = re.search(r'\[([^,]+), \{', output)
  if match:
    return float(match.group(1))
  else:
    return output

def get_expected(filename):
  with open(filename, 'r') as f:
    match = re.search(r'\#[ ]*answer:[ ]*([^ \n]+)', f.read())
    if match:
      return float(match.group(1))
    else:
      return "unknown"

def compare_result(result, expected):
  if expected == "unknown":
    return 'UNKNOWN'
  if result < expected:
    return 'FAILED'
  if result < expected*1.2:
    return 'CLOSE'
  else:
    if result == float("inf") and expected == float("inf"):
      return 'CLOSE'
    else:
      return 'FAR'
  

# integer constants
PASSED = 0; TIMEDOUT = 1; UNKNOWN = 2; FAILED = -1;
def process_test(cmd, test, expected, log_file):
  """
  This is the worker function for each process. This function process the supplied
  test and returns a tuple containing  indicating the test results.

  :return: A tuple with the
  """
  cmd = " ".join(cmd)
  str_result = "{}\n".format(cmd)

  t0 = time.time()
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err  = p.communicate()
  out = out.decode('utf-8')
  err = err.decode('utf-8')
  elapsed = time.time() - t0

  # get the test results
  result = get_result(out+err)
  if type(result) == type(float()):
    state = compare_result(result, expected)
    if state == 'UNKNOWN':
      str_result += red('UNKNOWN', log_file)
    elif state == 'FAILED':
      str_result += red('FAILED', log_file)
    elif state == 'FAR':
      str_result += yellow('FAR', log_file)
    elif state == 'CLOSE':
      str_result += green(state, log_file)
    else:
      str_result += state
  else:
    str_result += red('FAILED', log_file)

  # name = path.splitext(path.basename(test))[0]          
  #with open("{}-{}-{}-output.txt".format(path.dirname(test)+'/'+name, memory, verifier), 'w') as f:
    #f.write(' '.join(cmd)+"\n\n"+out+err)
  str_result += '\nAnswer: {} \nExpected: {}\nTime: {}\n\n'.format(result, expected, elapsed)
  return str_result


close = far = failed = unknowns = total = 0
def tally_result(result):
  """
  Tallies the result of each worker. This will only be called by the main thread.
  """
  # log the info
  logging.info(result)

  global close, far, failed, unknowns
  if "CLOSE" in result:
    close += 1
  elif "FAR" in result:
    far += 1
  elif "FAILED" in result:
    failed += 1
  elif "UNKNOWN" in result:
    unknowns += 1

def main():
  """
  Main entry point for the test suite.
  """
  global skipped, total
  
  t0 = time.time()
  num_cpus = multiprocessing.cpu_count()//2

  # configure the CLI
  parser = argparse.ArgumentParser()
  parser.add_argument("--threads", action="store", dest="n_threads", default=num_cpus, type=int,
                      help="execute regressions using the selected number of threads in parallel")
  parser.add_argument("--exe", type=str, help="What executable to run")
  parser.add_argument("--log", action="store", dest="log_level", default="DEBUG", type=str,
                      help="sets the logging level (DEBUG, INFO, WARNING)")
  parser.add_argument("--output-log", action="store", dest="log_path", type=str,
                      help="sets the output log path. (std out by default)")
  parser.add_argument("benchmark_dir")
  args = parser.parse_args()

  # configure the logging
  log_format = ''
  log_level = logging.DEBUG

  # change mode
  if not args.exe:
    exe = "gelpia"
    exten = ".txt"
  else:
    exe = args.exe
    if path.basename(args.exe) == "dop_gelpia":
      exten = ".dop"
    else:
      exten = ".txt"

  
  # add more log levels later (if needed)
  if args.log_level.upper() == "INFO":
    log_level = logging.INFO
  elif args.log_level.upper() == "WARNING":
    log_level = logging.WARNING

  # if the user supplied a log path, write the logs to that file.
  # otherwise, write the logs to std out.
  if args.log_path:
    logging.basicConfig(filename=args.log_path, format=log_format, level=log_level)
  else:
    logging.basicConfig(format=log_format, level=log_level)

  logging.debug("Creating Pool with '%d' Workers" % args.n_threads)
  p = ThreadPool(processes=args.n_threads)

  try:
    # start the tests
    logging.info("Running benchmarks...")

    # start processing the tests.
    results = []
    tests = sorted(glob.glob(os.path.join(args.benchmark_dir,"*"+exten)))
    total = len(tests)

    logging.info("{} benchmarks to process".format(total))

    for test in tests:
      
      # build up the subprocess command
      filename = ("" if path.basename(exe)=="dop_gelpia" else '@')+test
      cmd = [exe, filename, "-t 60"]
      expected = get_expected(test)

      if False:#"bad hack ian should remove":
        tally_result(process_test(cmd[:], test, expected, args.log_path,))
      else:
        r = p.apply_async(process_test,
                          args=(cmd[:], test, expected, args.log_path,),
                          callback=tally_result)
        results.append(r)

    # keep the main thread active while there are active workers
    for r in results:
      r.wait()

  except KeyboardInterrupt:
    logging.debug("Caught KeyboardInterrupt, terminating workers")
    p.terminate() # terminate any remaining workers
    p.join()
  else:
    logging.debug("Quitting normally")
    # close the pool. this prevents any more tasks from being submitted.
    p.close()
    p.join() # wait for all workers to finish their tasks

  # log the elapsed time
  elapsed_time = time.time() - t0
  logging.info(' ELAPSED TIME [%.2fs]' % round(elapsed_time, 2))

  # log the test results
  logging.info(' CLOSE   count: %d' % close)
  logging.info(' FAR     count: %d' % far)
  logging.info(' FAILED  count: %d' % failed)
  logging.info(' UNKNOWN count: %d' % unknowns)
  logging.info('\n TOTAL count: %d' % total)

  if (total != (close + far + failed + unknowns)):
    logging.info(red("ERROR:", None)+"number of tests does not equal total, there is a bug in regtest.py")


if __name__=="__main__":
  main()

