#!/bin/bash

# assumes it is being called in ssnetserver top directory

git submodule init
git submodule update

# ROOT
source /usr/local/bin/thisroot.sh

#opencv
export OPENCV_INCDIR=/usr/local/include
export OPENCV_LIBDIR=/usr/local/lib

source configure.sh

cd larlite
make
cd UserDev/BasicTool
make

cd ../../../Geo2D
make

cd ../larcv1
make

cd ..
