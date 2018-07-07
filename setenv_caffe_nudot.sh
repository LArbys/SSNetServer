#!/bin/bash

# ROOT
source /home/taritree/setup_root6.sh

#opencv
export OPENCV_INCDIR=/usr/local/include
export OPENCV_LIBDIR=/usr/local/lib

# cuda
export CUDA_INCDIR=/usr/local/cuda-8.0/targets/x86_64-linux/include
export CUDA_LIBDIR=/usr/local/cuda-8.0/targets/x86_64-linux/lib

# caffe
export CAFFE_DIR=/home/taritree/software/ssnet_example/sw/caffe/
export CAFFE_LIBDIR=${CAFFE_DIR}/build/lib
export CAFFE_INCDIR=${CAFFE_DIR}/build/include
export CAFFE_BINDIR=${CAFFE_DIR}/build/tools
export CAFFE_PYTHONDIR=${CAFFE_DIR}/python


[[ ":$PATH:" != *":${CAFFE_BINDIR}:"* ]] && PATH="${CAFFE_BINDIR}:${PATH}"
[[ ":$LD_LIBRARY_PATH:" != *":${CAFFE_LIBDIR}:"* ]] && LD_LIBRARY_PATH="${CAFFE_LIBDIR}:${LD_LIBRARY_PATH}"
if [ -z ${PYTHONPATH+x} ]; then
    PYTHONPATH=.:${CAFFE_PYTHONDIR};
else
    [[ ":$PYTHONPATH:" != *":${CAFFE_PYTHONDIR}:"* ]] && PYTHONPATH="${CAFFE_PYTHONDIR}:${PYTHONPATH}";
fi

cd larlite
source config/setup.sh

cd ../larcv1
source configure.sh

cd ..
