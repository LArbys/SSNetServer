#!/bin/bash

imgname=singularity-ssnetserver-caffelarbys-cuda8.0.img

rm -f $imgname
sudo singularity build ${imgname} SingularityNoDirvers
