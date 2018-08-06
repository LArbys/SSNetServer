#!/bin/bash

SSS_BASEDIR=$1 # where the ssnetserver repo is
WORKDIR=$2     # Folder where files can be written
BROKER=$3      # IP ADDRESS OF BROKER
PORT=$4        # BROKER PORT FOR CLIENTS
SSNETOUT=$5    # OUTPUT PATH FOR SSNET FILE
TAGGERIN=$6    # INPUT PATH FOR TAGGER FILE
TREENAME=$7    # image2d treename


export OMP_NUM_THREADS=1
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS}"

# SETUP CONTAINER
cd ${SSS_BASEDIR}/container
source setup_caffelarbys_container.sh

# setup workdir
cd $WORKDIR
jobdir=`printf caffeclient_jobid%d ${SLURM_JOBID}`
local_outfile=`printf output_caffeclient_jobid%d.root ${SLURM_JOBID}`

# setup job folder
mkdir -p ${jobdir}
cp ${SSS_BASEDIR}/*.cfg ${jobdir}/
chmod -R g+rws ${jobdir}
cd ${jobdir}

# run the job
echo "start_caffe_client.py --identity ${SLURM_JOBID} --broker ${BROKER} -p ${PORT} -f ${TAGGERIN} -o ${local_outfile} -t ${TREENAME} --croi"
start_caffe_client.py --identity ${SLURM_JOBID} --broker ${BROKER} -p ${PORT} -f ${TAGGERIN} -o ${local_outfile} -t ${TREENAME} --croi || exit

# copy the output file
cp ${local_outfile} ${SSNETOUT}
rm *.root

# clean up
cd ${WORKDIR}
#rm -r ${jobdir}

