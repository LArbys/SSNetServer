#!/bin/bash
#
#SBATCH --job-name=ssn_workers
#SBATCH --output=ssn_workers.log
#SBATCH --ntasks=4
#SBATCH --mem-per-cpu=8000
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=2
#SBATCH --partition gpu
#SBATCH --nodelist=pgpu03

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-cuda8.0-nvidia384.66.img
WORKDIR=/usr/local/ssnetserver

# IP ADDRESSES OF BROKER
BROKER=10.246.81.73 # PGPU03
# BROKER=10.X.X.X # ALPHA001

PORT=5560

GPU_ASSIGNMENTS=/cluster/kappa/wongjiradlab/twongji01/ssnetserver/container/gpu_assignments.txt

module load singularity
singularity exec ${CONTAINER} bash -c "cd ${WORKDIR} && ./run_caffe1worker.sh ${WORKDIR} ${BROKER} ${PORT} ${GPU_ASSIGNMENTS}"
