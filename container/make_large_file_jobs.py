import os,sys
import argparse
import ROOT as rt
from larcv import larcv

if __name__ == "__main__":

    parser = argparse.ArgumentParser( description='make job file from one large ROOT file' )
    parser.add_argument( "-f", "--input-file", required=True, type=str, help="input ROOT file" )
    parser.add_argument( "-t", "--tree-name", required=True, type=str, help="tree name from which to get number of entries")
    parser.add_argument( "-n", "--num-jobs", required=True, type=int, help="number of jobs to be split into" )

    args = parser.parse_args( sys.argv[1:] )

    jobfile = open( 'joblist.txt', 'w' )

    tf = rt.TFile( args.input_file, 'open' )
    tt = tf.Get( "image2d_"+args.tree_name+"_tree" )

    if tt is None:
        print "Could not find tree, \'%s\', in %s"%(args.tree_name, args.input_file)
        sys.exit(-1)

    num_entries = tt.GetEntries()
    entries_per_job = num_entries/args.num_jobs
    num_jobs = args.num_jobs
    if num_entries%num_jobs!=0:
        num_jobs += 1


    print "Number of entries in file: ",num_entries
    print "Number of jobs to process file: ",num_jobs
    print "Number of entries per job: ",entries_per_job

    for ijob in range(0,num_jobs):
        start = ijob*entries_per_job
        end   = (ijob+1)*entries_per_job
        if end>num_entries:
            end = num_entries
        print >> jobfile,args.input_file,' ',start,' ',end

    jobfile.close()

    tf.Close()
