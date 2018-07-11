from __future__ import print_function

import os
import multiprocessing
import zmq
from larcv import larcv

from ssnetserver.caffelarcv1client import CaffeLArCV1Client
from ssnetserver.caffelarcv1worker import CaffeLArCV1Worker
from ssnetserver.server import SSNetBroker

NBR_CLIENTS=1
NBR_WORKERS=1

pname = os.popen('uname -n')
machine = pname.readlines()[0]

def start_client(ident,fname_in, fname_out,batchsize):
    products = {larcv.kProductImage2D:"modimg"}
    client = CaffeLArCV1Client(fname_in, fname_out, batchsize, ident, "localhost", products, process_croi=True )
    #client.process_events()
    client.process_events(0,3)
    client.io_out.finalize()
    client.print_time_tracker()

def start_worker(ident,machine):
    # because I am lazy I have saved some machine-specific configs,
    #  so I don't have to update this file everytime I switch machines.
    print("SETTING UP WORKER FOR %s"%(machine))
    if machine.strip()=="nunet":
        print("nunet setup")
        worker = CaffeLArCV1Worker(ident,"localhost", gpuid=1, weight_dir="/mnt/disk0/taritree/larbys/ssnet_dllee_trainingdata/", model_dir="/tmp/", print_msg_size=True) # nudot
    elif machine.strip()=="meitner":
        print("meitner setup")
        worker = CaffeLArCV1Worker(ident,"localhost", gpuid=1, weight_dir="/tmp",model_dir="/tmp/", print_msg_size=True) # meitner
    else:
        print("default")
        worker = CaffeLArCV1Worker(ident,"localhost", gpuid=1, weight_dir="/tmp",model_dir="/tmp/", print_msg_size=True) # meitner
    worker.do_work()

def main():

    # initialize broker
    broker = SSNetBroker("*")

    # define starter function
    def start(task,*args):
        process = multiprocessing.Process(target=task,args=args)
        process.daemon = True
        process.start()

    # start up clients
    for i in range(NBR_CLIENTS):
        # precropped examples
        #start(start_client,i,"/media/hdd1/larbys/ssnet_dllee_trainingdata/test_1e1p_lowE_00.root","output_test_caffe.root",1) # meitner
        #start(start_client,i,"/tmp/test_1e1p_lowE_00.root","output_test_caffe.root",1)
        
        # 
        #start(start_client,i,"/mnt/disk0/taritree/larbys/ssnet_dllee_trainingdata/test_1e1p_lowE_00.root","output_test_caffe.root",1) # nudot
        #start(start_client,i,"taggerout-larcv-Run006865-SubRun000047.root","output_test_caffe.root",1) # nudotx
        start(start_client,i,"ssnetout-larcv-Run000001-SubRun000006.root","output_test_caffe.root",1)
        
    # start up workers
    for i in range(NBR_WORKERS):
        start(start_worker,i,machine)

    broker.start(-1.0)
    broker.stop()


if __name__ == "__main__":

    main()
