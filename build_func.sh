#! /bin/bash

set -e

cd src/func && ./comp_comm.sh $1

cd ../..

cp src/func/target/release/libfunc_$1.so ./.compiled

