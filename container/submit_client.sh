#!/bin/bash
#
#SBATCH --job-name=ssn_server
#SBATCH --output=ssn_server.log
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=1
#SBATCH --nodelist=pgpu03

CONTAINER=/cluster/kappa/90-days-archive/wongjiradlab/larbys/images/singularity-ssnetserver/singularity-ssnetserver-cuda8.0-nvidia384.66.img
WORKDIR=/usr/local/ssnetserver

module load singularity
singularity exec ${CONTAINER} bash -c "cd ${WORKDIR}/container && source setup_container.sh && ./run_broker.sh"
