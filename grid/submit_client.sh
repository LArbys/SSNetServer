#!/bin/bash
#
#SBATCH --job-name=ssn_client
#SBATCH --output=ssn_client_array.log
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=1
#SBATCH --array=14-15

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-caffelarbys-cuda8.0.img

#SSS_BASEDIR=/usr/local/ssnetserver
SSS_BASEDIR=/cluster/kappa/wongjiradlab/twongj01/ssnetserver
WORKDIR=/cluster/kappa/90-days-archive/wongjiradlab/larbys/grid_work_dir/ssnetserver_client
WORKDIR_IN_CONTAINER=/cluster/kappa/wongjiradlab/larbys/grid_work_dir/ssnetserver_client

# IP ADDRESSES OF BROKER
BROKER=10.246.81.73 # PGPU03
# BROKER=10.X.X.X # ALPHA001

PORT=5559
OUTDIR_IN_CONTAINER=${WORKDIR_IN_CONTAINER}/output
JOBLIST=${WORKDIR_IN_CONTAINER}/joblist.txt   # made with either make_large_file_jobs.py or make_jobs_from_inputdirs.py
RUNLIST=${WORKDIR_IN_CONTAINER}/rerunlist.txt # map of taskid to job: {line in file=taskid : value of job=line in joblist}
TREENAME=wire

mkdir -p ${WORKDIR}
module load singularity
singularity exec ${CONTAINER} bash -c "cd ${SSS_BASEDIR}/grid && ./run_caffe1client.sh ${SSS_BASEDIR} ${WORKDIR_IN_CONTAINER} ${BROKER} ${PORT} ${OUTDIR_IN_CONTAINER} ${JOBLIST} ${RUNLIST} ${TREENAME}"
