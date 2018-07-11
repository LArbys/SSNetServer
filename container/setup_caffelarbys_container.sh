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

# SSNET SERVER
#export SSNETSERVER_BASEDIR=/usr/local/ssnetserver
export SSNETSERVER_BASEDIR=/cluster/kappa/wongjiradlab/twongj01/ssnetserver
echo "SSNETSERVER_BASEDIR=${SSNETSERVER_BASEDIR}"

# Add Caffe to Paths
[[ ":$PATH:" != *":${CAFFE_BINDIR}:"* ]] && PATH="${CAFFE_BINDIR}:${PATH}"
[[ ":$LD_LIBRARY_PATH:" != *":${CAFFE_LIBDIR}:"* ]] && LD_LIBRARY_PATH="${CAFFE_LIBDIR}:${LD_LIBRARY_PATH}"
if [ -z ${PYTHONPATH+x} ]; then
    PYTHONPATH=.:${CAFFE_PYTHONDIR};
else
    [[ ":$PYTHONPATH:" != *":${CAFFE_PYTHONDIR}:"* ]] && PYTHONPATH="${CAFFE_PYTHONDIR}:${PYTHONPATH}";
fi

# Add SSNet Server to python path and path
[[ ":$PYTHONPATH:" != *":${SSNETSERVER_BASEDIR}:"* ]] && PYTHONPATH="${SSNETSERVER_BASEDIR}:${PYTHONPATH}";
[[ ":$PATH:" != *":${SSNETSERVER_BASEDIR}/bin:"* ]] && PATH="${SSNETSERVER_BASEDIR}/bin:${PATH}";

echo $PATH
echo $PYTHONPATH

# SETUP SSNET SERVER
cd ${SSNETSERVER_BASEDIR}
ls
echo "Configure deps"
source configure.sh
