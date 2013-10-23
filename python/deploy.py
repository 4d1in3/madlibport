import os
import sys

import optparse

import impala_util as iutil
from impala_util import impala, doit

'''
Compiles and registers UDAs with impala
'''




libs = [
    ('lib/libsvm.so', 'libsvm.so'),
    ('lib/libbismarckarray.so', 'bisarray.so'),
    ('lib/liblogr.so', 'liblogr.so'),
    ('lib/liblinr.so', 'liblinr.so')
    ]



queries = [
    #
    # Utilities
    #
    "DROP FUNCTION IF EXISTS arrayget(bigint, string)",
    "CREATE FUNCTION arrayget(bigint, string) returns double location '/user/cloudera/bisarray.so' SYMBOL='ArrayGet'",

    "DROP FUNCTION IF EXISTS toarray(double...);",
    "create FUNCTION toarray(double...) returns string location '/user/cloudera/bisarray.so' SYMBOL='_Z7ToArrayPN10impala_udf15FunctionContextEiPNS_9DoubleValE';",

    "DROP FUNCTION IF EXISTS allbytes();",
    "create FUNCTION allbytes() returns string location '/user/cloudera/bisarray.so' SYMBOL='AllBytes';",

    "DROP FUNCTION IF EXISTS printarray();",
    "create FUNCTION printarray(string) returns string location '/user/cloudera/bisarray.so' SYMBOL='PrintArray';",

    "DROP FUNCTION IF EXISTS encodearray(string);",
    "create FUNCTION encodearray(string) returns string location '/user/cloudera/bisarray.so' SYMBOL='EncodeArray';",
    "DROP FUNCTION IF EXISTS decodearray(string);",
    "create FUNCTION decodearray(string) returns string location '/user/cloudera/bisarray.so' SYMBOL='DecodeArray';",

    #
    # SVM
    #
    "DROP aggregate function IF EXISTS svm(string, string, boolean, double, double);",
    "create aggregate function svm(string, string, boolean, double, double) returns string location '/user/cloudera/libsvm.so' UPDATE_FN='SVMUpdate';"

    "DROP function IF EXISTS svmpredict(string, string);",
    "create function svmpredict(string, string) returns boolean location '/user/cloudera/libsvm.so' SYMBOL='SVMPredict';"

    "DROP function IF EXISTS svmloss(string, string, boolean);",
    "create function svmloss(string, string, boolean) returns double location '/user/cloudera/libsvm.so' SYMBOL='SVMLoss';"

    #
    # Logistic
    #
    "DROP aggregate function IF EXISTS logr(string, string, boolean, double, double);",
    "create aggregate function logr(string, string, boolean, double, double) returns string location '/user/cloudera/liblogr.so' UPDATE_FN='LogrUpdate';"

    "DROP function IF EXISTS logrpredict(string, string);",
    "create function logrpredict(string, string) returns boolean location '/user/cloudera/liblogr.so' SYMBOL='LogrPredict';"

    "DROP function IF EXISTS logrloss(string, string, boolean);",
    "create function logrloss(string, string, boolean) returns double location '/user/cloudera/liblogr.so' SYMBOL='LogrLoss';"

    #
    # Linear Regression
    #
    "DROP aggregate function IF EXISTS linr(string, string, double);",
    "create aggregate function linr(string, string, double) returns string location '/user/cloudera/liblinr.so' UPDATE_FN='LinrUpdate';"

    "DROP function IF EXISTS linrpredict(string, string);",
    "create function linrpredict(string, string) returns boolean location '/user/cloudera/liblinr.so' SYMBOL='LinrPredict';"

    ]

def main():
  parser = optparse.OptionParser('usage: %prog DATABASE')

  parser.add_option("-m", "--make",
                        action="store_true", dest="make", default=False,
                                          help="Remake the shared object files (calls make).")
  parser.add_option("-p", "--put",
                        action="store_true", dest="put", default=False,
                                          help="Put the the shared objects into HDFS")
  parser.add_option("-n", "--noact",
                        action="store_true", dest="noact", default=False,
                                          help="just print queries, don't execute over impala")

  (options, args) = parser.parse_args()

  if len(args) < 1:
    parser.print_usage()
    return

  # compile the lib*.so files
  if options.make:
    doit("make -B all")

  # put them into HDFS so impala can load them
  if options.put:
    for lb, tar in libs:
      doit('hadoop fs -rm /user/cloudera/%s' % tar, mayfail=True)
      doit('hadoop fs -mkdir -p /user/cloudera')
      doit('hadoop fs -put %s /user/cloudera/%s' % (lb, tar))

  # register the functions with impala
  for q in queries:
    print q
  if not options.noact:
    iutil.impala_shell_exec(queries, args[0])

if __name__ == '__main__':
  main()
