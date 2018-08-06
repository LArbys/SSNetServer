import os,sys,time
from worker import SSNetWorker
import numpy as np
import zlib
import zmq

from larcv import larcv

import msgpack
import msgpack_numpy as m
m.patch()

os.environ["GLOG_minloglevel"] = "1"
import caffe


from workermessages import decode_larcv1_metamsg


class CaffeLArCV1Worker( SSNetWorker ):
    """ This worker simply receives data and replies with dummy string. prints shape of array. """

    def __init__( self, identity,broker_ipaddress,
                  gpuid=0, weight_dir="/tmp", model_dir="/tmp", 
                  port=5560, heartbeat_interval_secs=2, num_missing_beats=3, timeout_secs=30,
                  ssh_thru_server=None, print_msg_size=False, reply_in_float16=True ):
        super( CaffeLArCV1Worker, self ).__init__(identity,broker_ipaddress,
                                                  port=port, heartbeat_interval_secs=heartbeat_interval_secs,
                                                  num_missing_beats=num_missing_beats, timeout_secs=timeout_secs,
                                                  ssh_thru_server=ssh_thru_server)
        self.shape_dict = {}

        # SSNET MODEL USED IN 2018 MICROBOONE PAPER
        #self.MODEL_PROTOTXT = "/home/twongj01/working/ubresnet/models/dllee_ssnet2018.prototxt"
        self.MODEL_DIR = model_dir        
        self.MODEL_PROTOTXT = self.MODEL_DIR+"/dllee_ssnet2018.prototxt"
        #self.WEIGHTS = [ "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane0_iter_75500.caffemodel",
        #                 "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane1_iter_65500.caffemodel",
        #                 "/home/twongj01/working/ubresnet/weights/ssnet2018caffe/segmentation_pixelwise_ikey_plane2_iter_68000.caffemodel" ]
        self.WEIGHT_DIR = weight_dir        
        self.WEIGHTS = [ self.WEIGHT_DIR+"/segmentation_pixelwise_ikey_plane0_iter_75500.caffemodel",
                         self.WEIGHT_DIR+"/segmentation_pixelwise_ikey_plane1_iter_65500.caffemodel",
                         self.WEIGHT_DIR+"/segmentation_pixelwise_ikey_plane2_iter_68000.caffemodel" ]
    
        # Number of Planes (should be three at most)
        self.NPLANES = 3

        # Tensor dimension sizes
        self.BATCHSIZE=1
        self.NCLASSES = 3
        self.WIDTH=None  # set later
        self.HEIGHT=None # set later
        self.GPUID=gpuid

        # compression level
        self.compression_level = 6

        # print msg size (for debug and cost estimation)
        self.print_msg_size = print_msg_size

        # reply in float16 (half-precision)
        self.reply_in_float16 = reply_in_float16
        
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
            x_comp = frames[i+2]
            x_enc  = zlib.decompress(x_comp)

            # decode frames
            
            # -- meta
            meta = decode_larcv1_metamsg( metamsg )
            
            # -- array
            arr = msgpack.unpackb(x_enc, object_hook=m.decode)

            key = (name,meta.plane())
            if key not in self.image_dict:
                self.image_dict[key] = {}
                self.meta_dict[key]  = {}                

            self.image_dict[key] = arr
            self.meta_dict[key]  = meta            
            self.shape_dict[key] = arr.shape
                
            print "CaffeLArCV1Worker[{}] received array name=\"{}\" shape={} meta={}".format(self._identity,name,arr.shape,meta.dump().strip())

        return "Thanks!"

    def generate_reply(self):
        """
        we run the network
        """
        
        reply = []
        totmsgsize = 0.0
        totcompsize = 0.0        
        for key,shape in self.shape_dict.items():

            name    = key[0]
            planeid = key[1]
            
            dummy = np.zeros( shape, dtype=np.float32 )
            meta  = self.meta_dict[key]
            img   = self.image_dict[key]

            msg_batchsize = shape[0]

            # prepare numpy array for output
            # note, we through away the background scores to save egress data
            # we save results in half-precision. since numbers between [0,1] precision still good to 2^-11 at worse
            if not self.reply_in_float16:
                ssnetout = np.zeros( (shape[0],self.NCLASSES-1,shape[2],shape[3]), dtype=np.float16 )
            else:
                ssnetout = np.zeros( (shape[0],self.NCLASSES-1,shape[2],shape[3]), dtype=np.float32 )

            blobshape = ( self.BATCHSIZE, 1, shape[2], shape[3] )

            # run the net for the plane
            self.nets[planeid].blobs['data'].reshape( *blobshape )

            # process the images
            for ibatch in range(0,msg_batchsize,self.BATCHSIZE):
                imgslice = img[ibatch*self.BATCHSIZE:(ibatch+1)*self.BATCHSIZE,:]
                self.nets[planeid].blobs['data'].data[...] = imgslice
                self.nets[planeid].forward()
                if (ibatch+1)*self.BATCHSIZE>msg_batchsize:
                    remaining = msg_batchsize % self.BATCHSIZE
                    start = ibatch*self.BATCHSIZE
                    end   = ibatch*self.BATCHSIZE+remaining
                    if self.reply_in_float16:                    
                        ssnetout[start:end,:] = self.nets[planeid].blobs['softmax'].data[0:remaining,:].astype(np.float16)
                    else:
                        ssnetout[start:end,:] = self.nets[planeid].blobs['softmax'].data[0:remaining,:]
                else:
                    start = ibatch*self.BATCHSIZE
                    end   = (ibatch+1)*self.BATCHSIZE
                    if self.reply_in_float16:
                        ssnetout[start:end,:] = self.nets[planeid].blobs['softmax'].data[0:self.BATCHSIZE,1:,:].astype(np.float16)
                    else:
                        ssnetout[start:end,:] = self.nets[planeid].blobs['softmax'].data[0:self.BATCHSIZE,1:,:]

                # we threshold score images so compression performs better
                outslice = ssnetout[start:end,:]
                for c in range(outslice.shape[1]):
                    chslice = outslice[:,c,:].reshape( (1,1,imgslice.shape[2],imgslice.shape[3]) )
                    chslice[ imgslice<10.0 ] = 0
                
            # encode
            x_enc = msgpack.packb( ssnetout, default=m.encode )
            x_comp = zlib.compress(x_enc,self.compression_level)

            # for debug: inspect compression gains (usually reduction to 1% or lower of original size)
            if self.print_msg_size:
                encframe = zmq.Frame(x_enc)
                comframe = zmq.Frame(x_comp)
                totmsgsize  += len(encframe.bytes)
                totcompsize += len(comframe.bytes)
                

            # make the return message
            print "CaffeLArCV1Worker[{}] preparing reply for name=\"{}\" shape={} meta={}".format(self._identity,name,ssnetout.shape,meta.dump().strip())

            reply.append( name.encode('utf-8') )
            reply.append( meta.dump().strip() )
            reply.append( x_comp )

        print "CaffeLArCV1Worker[{}] finished reply for name=\"{}\". size of array portion={} MB (uncompressed {} MB)".format(self._identity,name,totcompsize/1.0e6,totmsgsize/1.0e6)

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


    
