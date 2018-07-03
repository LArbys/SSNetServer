#!/bin/sh

rsync -av --progress /home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation* /tmp/
rsync -av --progress dllee_ssnet2018.prototxt /tmp/
