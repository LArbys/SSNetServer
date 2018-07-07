import time
from client import SSNetClient
from collections import OrderedDict
import ROOT as rt
from ROOT import std
from larcv import larcv
import numpy as np
import zmq
import zlib

import msgpack
import msgpack_numpy as m
m.patch()

from workermessages import decode_larcv1_metamsg

# Inherist from client.SSNetClient
# Base class handles network stuff
# This handles processing of LArCV1 events
# Really, what I should use is composition ...

class CaffeLArCV1Client( SSNetClient ):

    def __init__(self, input_rootfile, output_rootfile, batch_size, identity, broker_ipaddress, product_dict,
                 random_access=True, copy_input=False, port=5559, timeout_secs=30, max_tries=3, do_compress=True ):
        
        # Call Mother
        super( CaffeLArCV1Client, self ).__init__( identity, broker_ipaddress, port=port, timeout_secs=timeout_secs, max_tries=max_tries, do_compress=do_compress )

        # Now load ROOT File
        self.input_rootfile  = input_rootfile
        self.output_rootfile = output_rootfile
        if self.input_rootfile==self.output_rootfile:
            raise ValueError("input and output rootfiles are the same!")

        # setup input
        self.io = larcv.IOManager( larcv.IOManager.kREAD )
        self.io.add_in_file( self.input_rootfile )
        self.io.initialize()
        self.NPLANES = 3

        # setup output
        if not copy_input:
            self.io_out = larcv.IOManager( larcv.IOManager.kWRITE )
            self.io_out.set_out_file( self.output_rootfile )
            self.io_out.initialize()
        else:
            self.io_out = larcv.IOManager( larcv.IOManager.kBOTH )
            self.io_out.add_in_file( self.input_rootfile )
            self.io_out.set_out_file( self.output_rootfile )
            self.io_out.initialize()

        self.batch_size = batch_size
        self.nentries = self.io.get_n_entries()
        self.randomize = random_access
        self.last_entry = 0
        self.delivered = 0
        self.permuted = np.random.permutation( self.nentries )
        self.totserved = 0
        self.compression_level = 6

        if type(product_dict) is dict:
            self.product_dict=product_dict
        elif product_dict is None:
            pass
        else:
            raise ValueError("product_dict should be a dictionary of {larcv product enum:producer name }")

        # space for image data
        self.imgdata_shape = {}
        self.imgdata_dict = {}
        self.imgmeta_dict = {}
        self.batch2rse = None
        self.current_rse = None
        for ktype,producer_name in self.product_dict.items():
            if ktype!=larcv.kProductImage2D:
                raise RuntimeError("Does not support loading product id=%d, currently"%(ktype))
            self.imgdata_shape[(ktype,producer_name)] = None
            self.imgdata_dict[(ktype,producer_name)] = None
            self.imgmeta_dict[producer_name] = None

        # timing tracker
        self._ttracker["getbatch::indexing"] = 0.0
        self._ttracker["getbatch::total"] = 0.0
        self._ttracker["getbatch::fileio"] = 0.0
        self._ttracker["getbatch::fill"] = 0.0
        self._ttracker["makemessage::total"] = 0.0
        self._ttracker["savereply::total"] = 0.0
        

    def get_batch( self ):
        
        """ we grab 'batch_size' entries from the file """
        if self.batch_size > self.nentries:
            raise ValueError("batch_size>number of file entries not supported currently. make issue request on github if needed.")

        tindex = time.time()
        if self.randomize:
            if self.delivered+self.batch_size>=self.nentries:
                # refresh the permutated event indices
                self.permuted = np.random.permutation( self.nentries )
                # reset the delivered count
                self.delivered = 0
            indices = self.permuted[self.delivered:self.delivered+self.batch_size]
            
        else:
            # sequential
            if self.delivered+self.batch_size>=self.entries:
                self.permuted = np.arange( self.nentries, dtype=np.int )
                self.delivered = 0
        self._ttracker["getbatch::indexing"] += time.time()-tindex


        # prepare batch
        # -------------------------
        # eventually this needs to be a user defined function get(self.io). user defines function not config file.
        # right now, only support loading image array data
        tbatch = time.time()
        self.batch2rse = {} # map from batch to (run,subrun,event)
        for i,index in enumerate(self.permuted[self.delivered:self.delivered+self.batch_size]):

            print "batchindex=%d, entryindex=%d"%(i,index)
            
            # read entry
            tread = time.time()
            nbytes = self.io.read_entry( index )
            if nbytes<=0:
                raise RuntimeError("failure reading entry %d in file %s"%(index,self.larcv1_rootfile))

            # get event containers
            ev_containers = {}
            rse = None
            for ktype,producer_name in self.product_dict.items():
                try:
                    ev_data = self.io.get_data( ktype, producer_name )
                except:
                    raise RuntimeError("could not retrieve data product for product_id=%d and producername=%s"%(ktype,producer_name))
                ev_containers[(ktype,producer_name)] = ev_data
                if rse is None:
                    rse = ( ev_data.run(), ev_data.subrun(), ev_data.event() )
            self._ttracker["getbatch::fileio"] += time.time()-tread                

            # now we return them, based on type
            # for now, only support images and simple loading
            tfill = time.time()

            # get the eventid for this batch
            self.batch2rse[i] = rse
            for (ktype,producer_name),container in ev_containers.items():
                k = (ktype,producer_name) # key
                if ktype!=larcv.kProductImage2D:
                    raise RuntimeError("Do not support loading product id=%d, currently"%(ktype))

                # images
                img_v = [ np.transpose( larcv.as_ndarray(container.Image2DArray()[x]), (1,0) ) for x in range(container.Image2DArray().size()) ]
                
                # meta
                if self.imgmeta_dict[producer_name] is None:
                    self.imgmeta_dict[producer_name] = [ container.Image2DArray()[x].meta() for x in range(container.Image2DArray().size()) ]

                # store the arrays into self.imgdata_dict.
                # we split the planes, since they have different networks

                # if first time filling for this producer/name combo, create list of arrays for storage
                if self.imgdata_dict[k] is None or self.imgdata_dict[k][0].shape[0]!=self.batch_size:
                    self.imgdata_dict[k] = [ np.zeros( (self.batch_size, 1, img_v[x].shape[0], img_v[x].shape[1] ), dtype=np.float32 ) for x in range(self.NPLANES) ]
                # copy the image data into the batch array
                for p in range(self.NPLANES):
                    img = img_v[p]
                    self.imgdata_dict[k][p][i,0,:] = img
            self._ttracker["getbatch::fill"] += time.time()-tfill
        self.delivered += self.batch_size
        self._ttracker["getbatch::total"] += time.time()-tbatch

        for n,t in self._ttracker.items():
            if "getbatch" in n:
                print "%s : %.2f secs : %.2f secs/batch : %.2f secs/img"%(n, t, t/(self.delivered/self.batch_size), t/self.delivered)
                    
        return self.imgdata_dict

    def make_outgoing_message(self):
        """ 
        we assume get_batch has set self.imgdata_dict to contain image data arrays.
        we also assume that the worker knows the data thats coming to it. an application requires creating both the client and worker.
        this is because I do not want to deal with generating a generic message protocal right now.
        """

        tmsg = time.time()

        msg = []
        for (ktype,name),plane_img_v in self.imgdata_dict.items():
            meta_v  = self.imgmeta_dict[name]
            for p in range(self.NPLANES):
                data = plane_img_v[p]
                meta = meta_v[p]

                x_enc = msgpack.packb(data, default=m.encode)
                x_comp = zlib.compress(x_enc,self.compression_level)
                #frmsg = zmq.Frame(data=x_enc)
                #cmmsg = zmq.Frame(data=x_comp)
                #msg_size = len(frmsg.bytes)
                #com_size = len(cmmsg.bytes)
                
                msg.append( name )
                msg.append( meta.dump().strip() )
                msg.append( x_comp )                
                print "CaffeLArCV1Client[{}] sending array name=\"{}\" shape={} meta={}".format(self._identity,name,data.shape,meta.dump().strip())
                #print "CaffeLArCV1Client[{}] compression ratio: ",com_size/msg_size

        tmsg = time.time()-tmsg
        self._ttracker["makemessage::total"] += tmsg

        return msg
    

    def process_reply(self,frames):

        # message parts consist of ssnet output
        # one part contains a batch for one plane
        # we must collect data for all three planes for an event, before writing it to disk

        # by construction, one batch is for one event
        # one message contains one batch
        # this makes it a lot easier to understand
        # someone smarter can make general code

        treply = time.time()

        plane_img_v_dict = {}

        parts = len(frames)        
        for i in range(0,parts,3):
            name    = frames[i].decode("ascii")
            metamsg = frames[i+1]
            x_comp  = frames[i+2]
            x_enc   = zlib.decompress(x_comp)

            if name not in plane_img_v_dict:
                plane_img_v_dict[name] = [ std.vector("larcv::Image2D")() for x in range(self.NPLANES) ]

            meta = decode_larcv1_metamsg( metamsg )
            arr = msgpack.unpackb(x_enc, object_hook=m.decode)
            nbatches = arr.shape[0]
            print "CaffeLArCV1Client[{}] received array name=\"{}\" shape={} meta={} batchsize={}".format(self._identity,name,arr.shape,meta.dump().strip(),nbatches)            
            
            for ib in range(nbatches):
                # set the RSE
                rse = self.batch2rse[ib]                    
                self.current_rse = rse
                
                img = larcv.as_image2d_meta( np.transpose( arr[ib,0,:], (1,0) ), meta )
                print "fill ",name," meta=",meta.dump().strip()
                plane_img_v_dict[name][meta.plane()].push_back( img )

        # make output event containers
        print "CaffeLArCV1Client[{}] storing images".format(self._identity)
        for name,plane_img_v in plane_img_v_dict.items():
            print "name: ",name,plane_img_v
            for img_v in plane_img_v:
                print img_v
                print img_v.size()
                planeid = img_v.front().meta().plane()
                print "CaffeLArCV1Client[{}] storing name={} plane={}".format(self._identity,name,planeid)
                outname = "%s_plane%d"%(str(name.decode("ascii")),planeid)
                print "Filling event container: ",outname
                output_ev_container = self.io_out.get_data( larcv.kProductImage2D, outname )
                for iimg in range(img_v.size()):
                    output_ev_container.Append( img_v[iimg] )
        
        # save output entry
        self.io_out.set_id( rse[0], rse[1], rse[2] )
        self.io_out.save_entry()
        self.io_out.clear_entry()
        self.current_rse = rse
        
        treply = time.time()-treply 
        self._ttracker["savereply::total"] += treply
        
    def process_events(self, start=None, end=None):

        tprocess = time.time()
        if start is None:
            start = 0
        if end is None:
            end = self.nentries

        for ientry in range(start,end):
            ok = self.send_receive()
            if not ok:
                raise RuntimeError("Trouble processing event")

        tprocess = time.time()-tprocess
        print "Time to run CaffeLArCV1Client[{}]::process_events: %.2f secs (%.2f secs/event)".format(self._identity)%(tprocess,tprocess/(end-start))
        

            
            
            

                
                    
    
