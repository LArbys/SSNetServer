#!/bin/bash

imgname=singularity-ssnetserver-cuda8.0-nvidia384.66.img

rm -f $imgname
sudo singularity build ${imgname} Singularity
