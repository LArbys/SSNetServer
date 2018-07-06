#!/bin/bash

WORKDIR=/cluster/kappa/wongjiradlab/twongj01/ssnetserver/container
CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-cuda8.0-nvidia384.66.img
module load singularity
singularity exec ${CONTAINER} bash -c "source /usr/local/root/release/bin/thisroot.sh && cd ${WORKDIR} && python make_large_file_jobs.py -f $1 -t $2 -n $3"
