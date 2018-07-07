import os,sys
import argparse

from caffelarcv1worker import CaffeLArCV1Worker

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Caffe Worker')
    parser.add_argument( "-i", "--identity", required=True, type=int, help="worker-id" )
    parser.add_argument( "-b", "--broker", required=True, type=str, help="network address to broker" )
    parser.add_argument( "-p", "--port", required=True, type=int, help="port of broker" )
    parser.add_argument( "-g", "--gpuid", required=True, type=int, help="gpuid to run code")
    parser.add_argument( "-w", "--weight_dir", required=True, type=str, help="weight directory")
    parser.add_argument( "-m", "--model_dir", required=True, type=str, help="model directory")
    parser.add_argument( "-s", "--ssh",       default="",    type=str, help="tunnel through server via ssh")

    print sys.argv
    args = parser.parse_args( sys.argv[1:] )

    ssh = None
    if args.ssh!="":
        ssh = args.ssh
    
    worker = CaffeLArCV1Worker( args.identity, args.broker,
                                port=args.port, gpuid=args.gpuid, weight_dir=args.weight_dir, model_dir=args.model_dir,
                                ssh_thru_server=ssh )
    worker.do_work()

    print "Worker exiting"
    
