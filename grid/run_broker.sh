#!/bin/bash

WORKDIR=$1

cd /usr/local/ssnetserver/container
source setup_caffelarbys_container.sh

cd $WORKDIR

./start_broker.py -c 5559 -w 5560 --timestamp-file ssnetserver_broker_timestamp.txt

