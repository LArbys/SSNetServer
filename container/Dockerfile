FROM twongjirad/docker-caffe-larbys-dlee-ssnet

MAINTAINER taritree.wongjirad@tufts.edu

# SSNET SERVER DEPENDENCIES
RUN apt-get update && apt-get install -y \
    python-pip \
    python-zmq \
    python-skimage \    
    python-msgpack && \
    apt-get autoremove -y && apt-get clean -y && \
    pip install msgpack-numpy && \
    apt-get autoremove -y && apt-get clean -y && \
    cd /usr/local/ && git clone https://github.com/larbys/ssnetserver && \
    cd /usr/local/ssnetserver/ && \
    bash -c "source build.sh"    