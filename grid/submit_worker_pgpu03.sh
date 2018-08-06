#!/bin/bash
#
#SBATCH --job-name=ssn_workers_pgpu03
#SBATCH --output=ssn_workers_pgpu03.log
#SBATCH --mem-per-cpu=2000
#SBATCH --time=3-0:00:00
#SBATCH --cpus-per-task=1
#SBATCH --partition gpu
#SBATCH --nodelist=pgpu03
#SBATCH --array=0-16

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-caffelarbys-cuda8.0.img
SSS_BASEDIR=/cluster/kappa/wongjiradlab/twongj01/ssnetserver
WORKDIR=/cluster/kappa/wongjiradlab/larbys/pubs/dlleepubs/serverssnet

# IP ADDRESSES OF BROKER
BROKER=10.246.81.73 # PGPU03
# BROKER=10.X.X.X # ALPHA001

PORT=5560

# GPU LIST
#GPU_ASSIGNMENTS=/cluster/kappa/wongjiradlab/twongj01/ssnetserver/grid/gpu_assignments.txt
GPU_ASSIGNMENTS=/cluster/kappa/wongjiradlab/larbys/pubs/dlleepubs/serverssnet/tufts_pgpu03_assignments.txt

module load singularity
singularity exec --nv ${CONTAINER} bash -c "cd ${SSS_BASEDIR}/grid && ./run_caffe1worker.sh ${SSS_BASEDIR} ${WORKDIR} ${BROKER} ${PORT} ${GPU_ASSIGNMENTS}"
