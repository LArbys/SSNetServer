#!/bin/bash

WORKDIR=$1
BROKER=$2
PORT=$3
INPUT=$4
OUTPUT=$5

cd $WORKDIR
cd larlite
source config/setup.sh
cd ../larcv1
source configure.sh
cd ..

echo "python start_caffe_client.py -i 0 -b $BROKER -p $PORT -f ${INPUT} -o ${OUTPUT}"
python start_caffe_client.py -i 0 -b $BROKER -p $PORT -f ${INPUT} -o ${OUTPUT}

