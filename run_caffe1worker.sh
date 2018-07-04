#!/bin/bash


WORKDIR=$1
BROKER=$2
PORT=$3
GPUIDLIST=$4

cd $WORKDIR/container
source setup_container.sh

let "proc_line=${SLURM_PROCID}+1"
echo "sed -n ${proc_line}p ${GPUIDLIST}"
let gpuid=`sed -n ${proc_line}p ${GPUIDLIST}`
echo "GPUID ${gpuid}"

cd $WORKDIR

echo "python start_caffe_worker.py -i 0 -b $BROKER -p $PORT -g $gpuid -w /tmp -m /tmp"
python start_caffe_worker.py -i 0 -b $BROKER -p $PORT -g ${gpuid} -w /tmp -m /tmp


