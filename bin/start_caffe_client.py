#!/usr/bin/env python

import os,sys
import argparse
from larcv import larcv
from ssnetserver.caffelarcv1client import CaffeLArCV1Client

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Caffe Client')
    parser.add_argument( "-i", "--identity",    required=True, type=int, help="client-id" )
    parser.add_argument( "-b", "--broker",      required=True, type=str, help="network address to broker" )
    parser.add_argument( "-p", "--port",        required=True, type=int, help="port of broker" )
    parser.add_argument( "-t", "--treename",    required=True, type=str, help="image2d tree name" )
    parser.add_argument( "-f", "--input-file",  required=True, type=str, help="input larcv1 file" )
    parser.add_argument( "-o", "--output-file", required=True, type=str, help="output larcv1 file" )
    parser.add_argument( "-c", "--croi",  default=False, action='store_true', help="process CROI within event images" )
    parser.add_argument( "-s", "--start", default=-1, type=int, help="starting entry" )
    parser.add_argument( "-e", "--end",  default=-1, type=int, help="ending entry" )
    parser.add_argument( "-m", "--timeout", default=90, type=int, help="poller time in seconds") 
    parser.add_argument( "-x", "--ximgcfg", default="input_precropped_default.cfg", type=str, help="configuration file for LArCV Image Processor")

    args = parser.parse_args( sys.argv[1:] )

    input_croiprocessor_cfg="input_precropped_default.cfg"
    input_precropped_cfg="input_precropped_default.cfg"
    if args.croi:
        input_croiprocessor_cfg=args.ximgcfg
        print "using imgmod config=",input_croiprocessor_cfg
    else:
        input_precropped_cfg=args.ximgcfg
        print "using imgmod config=",input_precropped_cfg

    products = {larcv.kProductImage2D: args.treename }
    client = CaffeLArCV1Client( args.input_file, args.output_file, 1, args.identity, args.broker,
                                products, process_croi=args.croi, 
                                input_croiprocessor_cfg=input_croiprocessor_cfg,
                                input_precropped_cfg=input_precropped_cfg,
                                timeout_secs=args.timeout )

    start = None
    end = None
    if args.start>0:
        start = args.start
    if args.end>0:
        end = args.end

    client.process_events(start=start,end=end)
    client.io_out.finalize()

    client.print_time_tracker()
