#!/bin/bash

docker rmi -f twongjirad/ssnetcaffeserver:sss_larbys_cuda8.0 .
docker build -t twongjirad/ssnetcaffeserver:sss_larbys_cuda8.0 .
