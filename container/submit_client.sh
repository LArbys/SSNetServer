#!/bin/bash
#
#SBATCH --job-name=ssn_client
#SBATCH --output=ssn_client_array.log
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=1
#SBATCH --array=10-13

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-cuda8.0-nvidia384.66.img

WORKDIR_IN_CONTAINER=/cluster/kappa/wongjiradlab/twongj01/ssnetserver

# IP ADDRESSES OF BROKER
BROKER=10.246.81.73 # PGPU03
# BROKER=10.X.X.X # ALPHA001

PORT=5559
OUTDIR_IN_CONTAINER=${WORKDIR_IN_CONTAINER}/grid
JOBLIST=${WORKDIR_IN_CONTAINER}/container/joblist.txt   # made with either make_large_file_jobs.py or make_jobs_from_inputdirs.py
RUNLIST=${WORKDIR_IN_CONTAINER}/container/rerunlist.txt # map of taskid to job: {line in file=taskid : value of job=line in joblist}
TREENAME=wire

module load singularity
singularity exec ${CONTAINER} bash -c "cd ${WORKDIR_IN_CONTAINER}/container && ./run_caffe1client.sh ${WORKDIR_IN_CONTAINER} ${BROKER} ${PORT} ${OUTDIR_IN_CONTAINER} ${JOBLIST} ${RUNLIST} ${TREENAME}"
