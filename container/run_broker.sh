#!/bin/bash

WORKDIR=$1

cd container
source setup_container.sh

python start_broker.py -c 5559 -w 5560
