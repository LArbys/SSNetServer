#!/bin/bash

# SETUP ROOT
source /usr/local/bin/thisroot.sh

# SETUP CAFFE
export CAFFE_ROOT=/usr/local/larbys/ssnet_example/sw/caffe
export CAFFE_LIBDIR=${CAFFE_ROOT}/build/lib
export CAFFE_INCDIR=${CAFFE_ROOT}/build/include
export CAFFE_BINDIR=${CAFFE_ROOT}/build/tools
export CAFFE_PYTHONDIR=${CAFFE_ROOT}/python

# OPENCV
export OPENCV_INCDIR=/usr/local/include
export OPENCV_LIBDIR=/usr/local/lib

[[ ":$PATH:" != *":${CAFFE_BINDIR}:"* ]] && PATH="${CAFFE_BINDIR}:${PATH}"
[[ ":$LD_LIBRARY_PATH:" != *":${CAFFE_LIBDIR}:"* ]] && LD_LIBRARY_PATH="${CAFFE_LIBDIR}:${LD_LIBRARY_PATH}"
if [ -z ${PYTHONPATH+x} ]; then
    PYTHONPATH=.:${CAFFE_PYTHONDIR};
else
    [[ ":$PYTHONPATH:" != *":${CAFFE_PYTHONDIR}:"* ]] && PYTHONPATH="${CAFFE_PYTHONDIR}:${PYTHONPATH}";
fi

# SETUP SSNET SERVER
cd /usr/local/ssnetserver
source configure.sh
