#!/bin/bash

SSS_BASEDIR=$1
WORKDIR=$2
TIMESTAMP_FILE=$3

echo "To SSNet Server container folder: ${SSS_BASEDIR}/container"
cd ${SSS_BASEDIR}/container
echo "Setup container environment variables"
source setup_caffelarbys_container.sh

cd ${WORKDIR}
start_broker.py -c 5559 -w 5560 --timestamp-file ${TIMESTAMP_FILE}
