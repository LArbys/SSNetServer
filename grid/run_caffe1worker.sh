#!/bin/bash


WORKDIR=$1
BROKER=$2
PORT=$3
GPUIDLIST=$4

# Go to ssnetserver folder in container
cd $WORKDIR/container
# configure environment
source setup_container.sh

# get the gpuid for this task
let "proc_line=${SLURM_ARRAY_TASK_ID}+1"
echo "sed -n ${proc_line}p ${GPUIDLIST}"
let gpuid=`sed -n ${proc_line}p ${GPUIDLIST}`
echo "SLURM_PROCID ${SLURM_PROCID}"
echo "SLURM_ARRAY_TASK_ID ${SLURM_ARRAY_TASK_ID}"
echo "GPUID ${gpuid}"

# go back to ssnetserver folder
cd $WORKDIR

# start caffe worker
# model and weight files assumed to be copied to /tmp
echo "python start_caffe_worker.py -i ${SLURM_ARRAY_TASK_ID} -b $BROKER -p $PORT -g $gpuid -w /tmp -m /tmp"
python start_caffe_worker.py -i ${SLURM_ARRAY_TASK_ID} -b $BROKER -p $PORT -g ${gpuid} -w /tmp -m /tmp


