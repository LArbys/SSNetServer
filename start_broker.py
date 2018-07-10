#!/bin/env python

import os,sys
import argparse
from server import SSNetBroker

from time import localtime, strftime

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start SSNet Broker')
    parser.add_argument( "-c", "--client-port", required=True, type=int, help="worker port" )
    parser.add_argument( "-w", "--worker-port", required=True, type=int, help="client port" )
    parser.add_argument( "-t", "--timestamp-file", default="", type=str, help="create file with time when broker started" )    
    args = parser.parse_args( sys.argv[1:] )

    broker = SSNetBroker("*", frontendport=args.client_port, backendport=args.worker_port)

    if args.timestamp_file!="":
        start = time.time()
        with open(args.timestamp_file,'w') as f:
            strtime = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
            print >> f,strtime
            
    broker.start(-1.0)
    broker.stop()
    
