FROM twongjirad/docker-ubuntu16.04-root:6.12.04_cuda9.1

MAINTAINER taritree.wongjirad@tufts.edu

# MKL
RUN cd /tmp/ && wget https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    apt-get update && apt-get install -y apt-transport-https && \
    apt-key add GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    sh -c 'echo deb https://apt.repos.intel.com/mkl all main > /etc/apt/sources.list.d/intel-mkl.list' && \
    apt-get update && apt-get install -y intel-mkl-64bit-2018.3-051 && \
    apt-get autoremove -y && apt-get clean -y    
    
    
# OPENCV3.2
RUN apt-get update && \
    apt-get install -y build-essential \
    	    cmake \
    	    git \
    	    libavcodec-dev \
	    libavformat-dev \
    	    libdc1394-22-dev \
    	    libgtk2.0-dev \
    	    libjasper-dev \
    	    libjpeg-dev \
    	    libpng-dev \
   	    libswscale-dev \
    	    libtiff-dev \
    	    libtbb2 \
    	    libtbb-dev \
	    cuda-cublas-dev-9-1 \
    	    pkg-config \
    	    python-dev \
    	    python-numpy \
    	    python-pandas && \
     pip install root_numpy && \
     apt-get autoremove -y & apt-get clean -y & \
     mkdir -p /tmp/build && cd /tmp/ && \
     git clone https://github.com/Itseez/opencv source && cd source && \
     git checkout 3.4.1 && cd /tmp/build && \
     cmake -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/source && \
     make -j4 && make install -j4 && \
     rm -r /tmp/build && rm -r /tmp/source && \
     apt-get autoremove -y && apt-get clean -y
    

# CAFFE 
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    libboost-all-dev \
    libprotobuf-dev \
    protobuf-compiler \
    python-protobuf \
    libgoogle-glog-dev \
    libgflags-dev \
    python-gflags \
    libhdf5-dev && \
    apt-get autoremove -y && apt-get clean -y && \
    mkdir -p /usr/local/caffe && cd /usr/local/caffe && \
    git clone https://github.com/BVLC/caffe.git src && mkdir /usr/local/caffe/build && \
    cd /usr/local/caffe/build && \
    cmake -DBLAS=MKL -DUSE_OPENCV=ON -DUSE_CUDNN=ON -DUSE_LMDB=OFF -DUSE_LEVELDB=OFF ../src/ && \
    make all && make install && rm -r /usr/local/caffe/src

# SSNET SERVER DEPENDENCIES
RUN apt-get update && apt-get install -y \
    python-pip \
    python-zmq \
    python-msgpack && \
    apt-get autoremove -y && apt-get clean -y && \
    pip install msgpack-numpy && \
    apt-get autoremove -y && apt-get clean -y && \
    cd /usr/local/ && git clone https://github.com/larbys/ssnetserver && \
    cd /usr/local/ssnetserver/ && git submodule init && git submodule update && \
    cd larlite && bash -c "source /usr/local/root/release/bin/thisroot.sh && source config/setup.sh && make" && \
    cd ../larcv1 && bash -c "source /usr/local/root/release/bin/thisroot.sh && source configure.sh && make"
    