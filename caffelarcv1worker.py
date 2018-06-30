import os,sys,time
from worker import SSNetWorker
import numpy as np

from larcv import larcv

import msgpack
import msgpack_numpy as m
m.patch()

os.environ["GLOG_minloglevel"] = "1"
import caffe


from workermessages import decode_larcv1_metamsg


class CaffeLArCV1Worker( SSNetWorker ):
    """ This worker simply receives data and replies with dummy string. prints shape of array. """

    def __init__( self, identity,broker_ipaddress, port=5560, heartbeat_interval_secs=2, num_missing_beats=3):
        super( CaffeLArCV1Worker, self ).__init__(identity,broker_ipaddress, port=port, heartbeat_interval_secs=heartbeat_interval_secs, num_missing_beats=num_missing_beats)
        self.shape_dict = {}

        # SSNET MODEL USED IN 2018 MICROBOONE PAPER
        #self.MODEL_PROTOTXT = "/home/twongj01/working/ubresnet/models/dllee_ssnet2018.prototxt"
        self.MODEL_PROTOTXT = "dllee_ssnet2018.prototxt"
        self.WEIGHTS = [ "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane0_iter_75500.caffemodel",
                         "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane1_iter_65500.caffemodel",
                         "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane2_iter_68000.caffemodel" ]
    
        # Number of Planes (should be three at most)
        self.NPLANES = 3

        # Tensor dimension sizes
        self.BATCHSIZE=4
        self.NCLASSES = 3
        self.WIDTH=None  # set later
        self.HEIGHT=None # set later
        self.GPUID=0

        # SET THE GPUID
        caffe.set_mode_gpu()
        caffe.set_device(self.GPUID)

        # Load the networks
        self.nets = [ caffe.Net( self.MODEL_PROTOTXT, self.WEIGHTS[x], caffe.TEST ) for x in range(0,self.NPLANES) ]
        print "CaffeWorker[{}] Networks are loaded.".format(self._identity)
        
    def process_message(self, frames ):
        """ we expect a batch for each plane 
        """
        
        # remake arrays
        self.shape_dict = {}
        self.meta_dict  = {}
        self.image_dict = {}
        parts = len(frames)
        for i in range(0,parts,3):
            # parse frames
            name  = frames[i].decode("ascii")
            metamsg  = frames[i+1]
            x_enc = frames[i+2]

            # decode frames
            
            # -- meta
            meta = decode_larcv1_metamsg( metamsg )
            
            # -- array
            arr = msgpack.unpackb(x_enc, object_hook=m.decode)

            self.image_dict[name] = arr
            self.shape_dict[name] = arr.shape
            self.meta_dict[name]  = meta
                
            print "CaffeLArCV1Worker[{}] received array name=\"{}\" shape={} meta={}".format(self._identity,name,arr.shape,meta.dump().strip())

        return "Thanks!"

    def generate_reply(self):
        """
        we run the network
        """
        
        reply = []
        for name,shape in self.shape_dict.items():

            dummy = np.zeros( shape, dtype=np.float32 )
            meta  = self.meta_dict[name]
            img   = self.image_dict[name]
            shape = self.shape_dict[name]
            planeid = int( meta.plane() )

            msg_batchsize = shape[0]
            if msg_batchsize==self.BATCHSIZE:
                ssnetout = None
            else:
                ssnetout = np.zeros( shape, dtype=np.float32 )

            blobshape = ( self.BATCHSIZE, shape[1], shape[2], shape[3] )

            # run the net for the plane
            net[planeid].blobs['data'].reshape( blobshape )

            # process the images
            for ibatch in range(0,msg_batchsize,self.BATCHSIZE):            
                net[planeid].blobs['data'].data[...] = img[ibatch*self.BATCHSIZE:(ibatch+1)*self.BATCHSIZE,:]
                net[planeid].forward()
                if (ibatch+1)*self.BATCHSIZE>msg_batchsize:
                    remaining = msg_batchsize % self.BATCHSIZE
                    start = ibatch*self.BATCHSIZE
                    end   = ibatch*self.BATCHSIZE+remaining
                    ssnetout[start:end,:] = net[planeid].blob['softmax'].data[0:remaining,:]

            # encode
            x_enc = msgpack.packb( ssnetout, default=m.encode )

            # make the return message
            reply.append( name )
            reply.append( meta.dump().strip() )
            reply.append(x_enc)

        return reply
        
            

if __name__ == "__main__":
    """ test if net loads properly """

    from server import SSNetBroker
    import multiprocessing

    def start_worker(ident):
        worker = CaffeLArCV1Worker(ident,"localhost")
        worker.do_work()
        
    process = multiprocessing.Process(target=start_worker,args=(0,))
    process.daemon = True
    process.start()

        
    broker = SSNetBroker( "*" )
    broker.start(-1.0)
    broker.stop()


    
