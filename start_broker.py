#!/bin/env python
import os,sys
import argparse
from server import SSNetBroker


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start SSNet Broker')
    parser.add_argument( "-c", "--client-port", required=True, type=int, help="worker port" )
    parser.add_argument( "-w", "--worker-port", required=True, type=int, help="client port" )
    args = parser.parse_args( sys.argv[1:] )

    broker = SSNetBroker("*", frontendport=args.client_port, backendport=args.worker_port)
    broker.start(-1.0)
    broker.stop()
    
