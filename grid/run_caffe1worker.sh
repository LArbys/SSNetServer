#!/bin/bash

SSS_BASEDIR=$1
WORKDIR=$2
BROKER=$3
PORT=$4
GPUIDLIST=$5

# Go to ssnetserver folder in container
cd $SSS_BASEDIR/container
# configure environment
source setup_caffelarbys_container.sh

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
echo "start_caffe_worker.py -i ${SLURM_ARRAY_TASK_ID} -b $BROKER -p $PORT -g $gpuid -w /tmp -m /tmp"
start_caffe_worker.py -i ${SLURM_ARRAY_TASK_ID} -b $BROKER -p $PORT -g ${gpuid} -w /tmp -m /tmp


