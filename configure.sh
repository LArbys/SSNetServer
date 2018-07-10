#!/bin/bash

# assumes it is being called in ssnetserver top directory

# ROOT
source /usr/local/bin/thisroot.sh

#opencv
export OPENCV_INCDIR=/usr/local/include
export OPENCV_LIBDIR=/usr/local/lib

echo "<< setup larlite >>"
cd larlite
source config/setup.sh

echo "<< setup Geo2D >>"
cd ../Geo2D
source config/setup.sh

echo "<< setup larcv1 >>"
cd ../larcv1
source configure.sh

cd ..
