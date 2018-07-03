#!/bin/bash

# SETUP ROOT
source /usr/local/root/release/bin/thisroot.sh

# SETUP CAFFE
export CAFFE_ROOT=/usr/local/caffe/build/install
export CAFFE_BINDIR=${CAFFE_ROOT}/bin
export CAFFE_LIBDIR=${CAFFE_ROOT}/lib
export CAFFE_PYTHONDIR=${CAFFE_ROOT}/python

[[ ":$PATH:" != *":${CAFFE_BINDIR}:"* ]] && PATH="${CAFFE_BINDIR}:${PATH}"
[[ ":$LD_LIBRARY_PATH:" != *":${CAFFE_LIBDIR}:"* ]] && LD_LIBRARY_PATH="${CAFFE_LIBDIR}:${LD_LIBRARY_PATH}"
if [ -z ${PYTHONPATH+x} ]; then
    PYTHONPATH=.:${CAFFE_PYTHONDIR};
else
    [[ ":$PYTHONPATH:" != *":${CAFFE_PYTHONDIR}:"* ]] && PYTHONPATH="${CAFFE_PYTHONDIR}:${PYTHONPATH}";
fi

# SETUP SSNET SERVER
cd /usr/local/ssnetserver
cd larlite
source config/setup.sh

cd ../larcv1
source configure.sh
cd ../
