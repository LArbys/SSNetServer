from __future__ import print_function

import multiprocessing
import zmq

from simplelarcv1client import SimpleLArCV1Client
from dummylarcv1worker import DummyLArCV1Worker
#from simplelarcv1worker import SimpleLArCV1Worker
from server import SSNetBroker

from larcv import larcv

NBR_CLIENTS=1
NBR_WORKERS=1

def start_client(ident,fname_in, fname_out,batchsize):
    products = {larcv.kProductImage2D:"wire"}
    client = SimpleLArCV1Client(fname_in, fname_out, batchsize, ident, "localhost", products )
    msg = client.send_receive()
    client.io_out.finalize()

def start_worker(ident):
    worker = DummyLArCV1Worker(ident,"localhost")
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
        start(start_client,i,"supera-Run000001-SubRun000300.root","test.root",10)

    # start up workers
    for i in range(NBR_WORKERS):
        start(start_worker,i)

    broker.start(-1.0)
    broker.stop()


if __name__ == "__main__":

    main()
