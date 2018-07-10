#!/bin/bash

SSNETSERVER_BASEDIR=$1
WORKDIR=$2
TIMESTAMP_FILE=$3

cd ${SSNETSERVER_BASEDIR}/container
source setup_caffelarbys_container.sh

cd ${WORKDIR}
./start_broker.py -c 5559 -w 5560 --timestamp-file ${TIMESTAMP_FILE}
