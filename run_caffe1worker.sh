#!/bin/bash


WORKDIR=$1
BROKER=$2
PORT=$3

cd $WORKDIR
cd larlite
source config/setup.sh
cd ../larcv1
source configure.sh
cd ..

echo "python start_caffe_worker.py -i 0 -b $BROKER -p $PORT -g 0 -w /tmp -m /tmp"
python start_caffe_worker.py -i 0 -b $BROKER -p $PORT -g 0 -w /tmp -m /tmp


