from __future__ import print_function

import multiprocessing
import zmq

from testclient import TestClient
from testworker import TestWorker
from server import SSNetBroker

NBR_CLIENTS=30
NBR_WORKERS=5

def start_client(ident):
    client = TestClient(ident,"localhost")
    msg = client.send_receive()

def start_worker(ident):
    worker = TestWorker(ident,"localhost")
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
        start(start_client,i)

    # start up workers
    for i in range(NBR_WORKERS):
        start(start_worker,i)

    broker.start(-1.0)
    broker.stop()


if __name__ == "__main__":

    main()
