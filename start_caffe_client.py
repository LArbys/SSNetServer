import os,sys
import argparse
from larcv import larcv
from caffelarcv1client import CaffeLArCV1Client

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Caffe Client')
    parser.add_argument( "-i", "--identity",    required=True, type=int, help="client-id" )
    parser.add_argument( "-b", "--broker",      required=True, type=str, help="network address to broker" )
    parser.add_argument( "-p", "--port",        required=True, type=int, help="port of broker" )
    parser.add_argument( "-t", "--treename",    required=True, type=str, help="image2d tree name" )
    parser.add_argument( "-f", "--input-file",  required=True, type=str, help="input larcv1 file" )
    parser.add_argument( "-o", "--output-file", required=True, type=str, help="output larcv1 file" )
    parser.add_argument( "-s", "--start", default=-1, type=int, help="starting entry" )
    parser.add_argument( "-e", "--end",  default=-1, type=int, help="ending entry" )

    args = parser.parse_args( sys.argv[1:] )

    products = {larcv.kProductImage2D: args.treename }
    client = CaffeLArCV1Client( args.input_file, args.output_file, 1, args.identity, args.broker, products )

    start = None
    end = None
    if args.start>0:
        start = args.start
    if args.end>0:
        end = args.end

    client.process_events(start=start,end=end)
    client.io_out.finalize()

    client.print_time_tracker()
