#!/bin/bash
#
#SBATCH --job-name=ssn_server
#SBATCH --output=ssn_server.log
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=8000
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=3
#SBATCH --partition gpu
#SBATCH --nodelist=pgpu03

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-cuda8.0-nvidia384.66.img
WORKDIR=/usr/local/ssnetserver
#WORKDIR=/cluster/kappa/wongjiradlab/twongj01/ssnetserver

module load singularity
singularity exec ${CONTAINER} bash -c "cd ${WORKDIR}/grid && ./run_broker.sh ${WORKDIR}"
