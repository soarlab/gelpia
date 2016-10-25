#! /bin/bash
# When ran this should be in the bin directory

set -e

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

cd ${SCRIPTPATH}/../src/func && ./comp_comm.sh $1

cd ../..

cp src/func/target/release/deps/libfunc_$1.so ./.compiled

