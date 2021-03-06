#!/bin/bash

SSS_BASEDIR=$1 # where the ssnetserver repo is
WORKDIR=$2     # Folder where files can be written
BROKER=$3      # IP ADDRESS OF BROKER
PORT=$4        # BROKER PORT FOR CLIENTS
OUTDIR=$5      # DIRECTORY WHERE OUTPUT SHOULD GO
JOBLIST=$6     # LIST SPECIFIYING JOBS
RUNLIST=$7     # LIST MAPPING SLURM_PROCID
TREENAME=$8    # image2d treename

# SETUP CONTAINER
cd ${SSS_BASEDIR}/container
source setup_caffelarbys_container.sh

# get the gpuid for this task
let "proc_line=${SLURM_ARRAY_TASK_ID}+1"
let runline=`sed -n ${proc_line}p ${RUNLIST}`+1
jobinfo=`sed -n ${runline}p ${JOBLIST}`
echo "procid=${SLURM_PROCID}"
echo "taskid=${SLURM_ARRAY_TASK_ID}"
echo "jobinfo: ${jobinfo}"

IFS=' '
array=( $jobinfo )
inputfile=${array[0]}
start=${array[1]}
end=${array[2]}

# go to workdir
cd $WORKDIR
jobdir=`printf caffeclient_proc%d_task%d ${SLURM_PROCID} ${SLURM_ARRAY_TASK_ID}`
local_outfile=`printf output_caffeclient_proc%d_task%03d.root ${SLURM_PROCID} ${SLURM_ARRAY_TASK_ID}`
final_outfile=`printf %s/%s ${OUTDIR} ${local_outfile}`

# setup work environment
mkdir -p ${jobdir}
#cp /usr/local/ssnetserver/*.py ${jobdir}/
#cp /cluster/kappa/wongjiradlab/twongj01/ssnetserver/*.py ${jobdir}/
cp ${SSS_BASEDIR}/*.cfg ${jobdir}/
cd ${jobdir}

echo "start_caffe_client.py --identity ${SLURM_ARRAY_TASK_ID} --broker ${BROKER} -p $PORT -f ${inputfile} -o ${local_outfile} -s ${start} -e ${end} -t ${TREENAME}"
start_caffe_client.py --identity ${SLURM_ARRAY_TASK_ID} --broker ${BROKER} -p $PORT -f ${inputfile} -o ${local_outfile} -s ${start} -e ${end} -t ${TREENAME} >& log

cp ${local_outfile} ${final_outfile}
rm *.root

