import time
from client import SSNetClient
from collections import OrderedDict
from larcv import larcv
import numpy as np

import msgpack
import msgpack_numpy as m
m.patch()

# Inherist from client.SSNetClient
# Base class handles network stuff
# This handles processing of LArCV1 events
# Really, what I should use is composition ...

class SimpleLArCV1Client( SSNetClient ):

    def __init__(self, larcv1_rootfile, batch_size, identity, broker_ipaddress, product_dict,
                 random_access=True, port=5559, timeout_secs=30, max_tries=3, do_compress=True ):
        
        # Call Mother
        super( SimpleLArCV1Client, self ).__init__( identity, broker_ipaddress, port=port, timeout_secs=timeout_secs, max_tries=max_tries, do_compress=do_compress )

        # Now load ROOT File
        self.larcv1_rootfile = larcv1_rootfile
        self.io = larcv.IOManager( larcv.IOManager.kREAD )
        self.io.add_in_file( self.larcv1_rootfile )
        self.io.initialize()

        self.batch_size = batch_size
        self.nentries = self.io.get_n_entries()
        self.randomize = random_access
        self.last_entry = 0
        self.delivered = 0
        self.permuted = np.random.permutation( self.nentries )
        self.totserved = 0

        if type(product_dict) is dict:
            self.product_dict=product_dict
        elif product_dict is None:
            pass
        else:
            raise ValueError("product_dict should be a dictionary of {larcv product enum:producer name }")

        # space for image data
        self.imgdata_shape = {}
        self.imgdata_dict = {}
        for ktype,producer_name in self.product_dict.items():
            if ktype!=larcv.kProductImage2D:
                raise RuntimeError("Does not support loading product id=%d, currently"%(ktype))
            self.imgdata_shape[(ktype,producer_name)] = None
            self.imgdata_dict[(ktype,producer_name)] = None

        # timing tracker
        self.ttracker = OrderedDict()
        self.ttracker["getbatch::indexing"] = 0.0
        self.ttracker["getbatch::total"] = 0.0
        self.ttracker["getbatch::fileio"] = 0.0
        self.ttracker["getbatch::fill"] = 0.0
        

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
        self.ttracker["getbatch::indexing"] += time.time()-tindex


        # prepare batch
        # -------------------------
        # eventually this needs to be a user defined function get(self.io). user defines function not config file.
        # right now, only support loading image array data
        for i,index in enumerate(self.permuted[self.delivered:self.delivered+self.batch_size]):

            print "batchindex=%d, entryindex=%d"%(i,index)
            
            # read entry
            tread = time.time()
            nbytes = self.io.read_entry( index )
            if nbytes<=0:
                raise RuntimeError("failure reading entry %d in file %s"%(index,self.larcv1_rootfile))

            ev_containers = {}
            for ktype,producer_name in self.product_dict.items():
                try:
                    ev_data = self.io.get_data( ktype, producer_name )
                except:
                    raise RuntimeError("could not retrieve data product for product_id=%d and producername=%s"%(ktype,producer_name))
                ev_containers[(ktype,producer_name)] = ev_data
            self.ttracker["getbatch::fileio"] += time.time()-tread                

            # now we return them, based on type
            # for now, only support images and simple loading
            ev_data = {}
            for (ktype,producer_name),container in ev_containers.items():
                k = (ktype,producer_name) # key
                if ktype!=larcv.kProductImage2D:
                    raise RuntimeError("Do not support loading product id=%d, currently"%(ktype))

                # images
                img_v = [ np.transpose( larcv.as_ndarray(container.Image2DArray()[i]), (1,0) ) for i in range(container.Image2DArray().size()) ]
                ev_data[ k ] = img_v

                if self.imgdata_dict[k] is None or self.imgdata_dict[k].shape[0]!=self.batch_size:
                    self.imgdata_dict[k] = np.zeros( (self.batch_size, 1, img_v[0].shape[0], img_v[0].shape[1] ), dtype=np.float32 )
                for img in img_v:
                    self.imgdata_dict[k][i,0,:] = img[:]
                    
        return self.imgdata_dict

    def make_outgoing_message(self):
        """ 
        we assume get_batch has set self.imgdata_dict to contain image data arrays.
        we also assume that the worker knows the data thats coming to it. an application requires creating both the client and worker.
        this is because I do not want to deal with generating a generic message protocal right now.
        """

        msg = []
        for (ktype,name),data in self.imgdata_dict.items():
            x_enc = msgpack.packb(data, default=m.encode)
            msg.append( name )
            msg.append( x_enc )

        return msg
    
                
                
            

            
            
            

                
                    
    
