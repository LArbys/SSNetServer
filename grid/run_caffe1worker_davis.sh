#!/bin/bash

SSS_BASEDIR=/home/taritree/working/ssnetserver
WORKDIR=/home/taritree/working/ssnetserver/grid
BROKER=10.246.81.73
PORT=5560
GPUIDLIST=/home/taritree/working/ssnetserver/grid/davis_gpu_assignments.txt
WORKER_OFFSET=500
PID=$1

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
#for PID in 0 1 2 3
#do
let "WORKER_ID=${WORKER_OFFSET}+${PID}"
echo "start_caffe_worker.py -i ${WORKER_ID} -b $BROKER -p $PORT -g $gpuid -w /tmp -m /tmp"
start_caffe_worker.py -i ${WORKER_ID} -b $BROKER -p $PORT -g ${gpuid} -w /tmp -m /tmp --ssh twongj01@fastx-dev.cluster.tufts.edu
#done


