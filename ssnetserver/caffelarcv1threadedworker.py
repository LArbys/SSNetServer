import os,sys,time
import multiprocessing
import threading
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

class PlaneNetworkWorker(threading.Thread):

    def __init__(self, context, identity, planeid, gpuid, weightfile, modelfile ):
        """ This class is to be run on a separate thread """
        super(PlaneNetworkWorker,self).__init__()
        
        # bind sockets
        self._context  = context

        # socket from main thread to network (this) thread
        self._incoming = self._context.socket(zmq.SUB)
        self._incoming.connect("inproc://worker{}_incoming".format(identity))
        self._incoming.setsockopt(zmq.SUBSCRIBE,"plane%d"%(planeid)) # subscribe only to plane messages

        # socket from network thread back to main thread
        self._outgoing = self._context.socket(zmq.PUB)
        self._outgoing.sndhwm = 1100000
        self._outgoing.bind("inproc://worker{}_plane{}_outgoing".format(identity,planeid))

        # socket to sync with main thread
        self._sync = self._context.socket(zmq.REQ)
        self._sync.connect("inproc://synctomain{}".format(identity))
        
        # config
        self.reply_in_float16 = True
        self.BATCHSIZE = 1
        self.NCLASSES = 3
        self.PLANEID = planeid
        self._identity = identity
        self._gpuid = gpuid
        self._modelfile = modelfile
        self._weightfile = weightfile
        self._compression_level = 6
        

    def run(self):

        # set to gpu
        caffe.set_mode_gpu()
        caffe.set_device(self._gpuid)

        # Load the networks
        self.net = caffe.Net( self._modelfile, self._weightfile, caffe.TEST )
        
        # sync with main PUB thread
        #print "PlaneNetworkWorker[{}]::Plane[{}]::Run sync with main thread-[{}]".format(self._identity,self.PLANEID,self._identity)        
        self._sync.send(b'')
        self._sync.recv()
        
        #print "PlaneNetworkWorker[{}]::Plane[{}] synced and setup".format(self._identity,self.PLANEID)
        
        # we get an image from the main thread
        while True:
            # wait for an image from the main thread
            # should be an image
            #print "PlaneNetworkWorker[{}]::Plane[{}] wait for message".format(self._identity,self.PLANEID)
            frames = self._incoming.recv_multipart()
            #print "PlaneNetworkWorker[{}]::Plane[{}] message arrived. Processing".format(self._identity,self.PLANEID)            
            reply = self.process_image(frames[1:])
            #print "PlaneNetworkWorker[{}]::Plane[{}] sending reply".format(self._identity,self.PLANEID)
            self._outgoing.send_multipart( reply )

    def process_image(self,frames):
        
        # parse frames
        name  = frames[0]
        metamsg  = frames[1]
        x_comp = frames[2]
        x_enc  = zlib.decompress(x_comp)

        # decode frames
            
        # -- meta
        meta = decode_larcv1_metamsg( metamsg )
            
        # -- array
        arr = msgpack.unpackb(x_enc, object_hook=m.decode)
        shape = arr.shape

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
        #print "PlaneNetworkWorker[{}]::Plane[{}]: processing {}".format(self._identity,self.PLANEID,name)
        self.net.blobs['data'].reshape( *blobshape )
        
        # process the images
        for ibatch in range(0,msg_batchsize,self.BATCHSIZE):
            imgslice = arr[ibatch*self.BATCHSIZE:(ibatch+1)*self.BATCHSIZE,:]
            self.net.blobs['data'].data[...] = imgslice
            tforward = time.time()
            #print "PlaneNetworkWorker[{}]::Plane[{}]: forward".format(self._identity,self.PLANEID)
            self.net.forward()
            tforward = time.time() - tforward
            #print "PlaneNetworkWorker[{}]::Plane[{}]: network returns after %.03f secs".format(self._identity,self.PLANEID)%(tforward) 
            # copy predictions to ssnetout
            if (ibatch+1)*self.BATCHSIZE>msg_batchsize:
                remaining = msg_batchsize % self.BATCHSIZE
                start = ibatch*self.BATCHSIZE
                end   = ibatch*self.BATCHSIZE+remaining
                if self.reply_in_float16:                    
                    ssnetout[start:end,:] = self.net.blobs['softmax'].data[0:remaining,:].astype(np.float16)
                else:
                    ssnetout[start:end,:] = self.net.blobs['softmax'].data[0:remaining,:]
            else:
                start = ibatch*self.BATCHSIZE
                end   = (ibatch+1)*self.BATCHSIZE
                if self.reply_in_float16:
                    ssnetout[start:end,:] = self.net.blobs['softmax'].data[0:self.BATCHSIZE,1:,:].astype(np.float16)
                else:
                    ssnetout[start:end,:] = self.net.blobs['softmax'].data[0:self.BATCHSIZE,1:,:]

            # we threshold score images so compression performs better
            outslice = ssnetout[start:end,:]
            for c in range(outslice.shape[1]):
                chslice = outslice[:,c,:].reshape( (1,1,imgslice.shape[2],imgslice.shape[3]) )
                chslice[ imgslice<5.0 ] = 0
                
        # encode
        x_enc = msgpack.packb( ssnetout, default=m.encode )
        x_comp = zlib.compress(x_enc,self._compression_level)
        
        # make the return message
        #print "PlaneNetworkWorker[{}]::Plane[{}] processed name=\"{}\" shape={} meta={}".format(self._identity,self.PLANEID,name,ssnetout.shape,meta.dump().strip())
        reply = ["plane%d"%(self.PLANEID)] # topic frame
        reply.append( name.encode('utf-8') )
        reply.append( meta.dump().strip() )
        reply.append( x_comp )

        return reply
            


def start_worker( context, identity, planeid, gpuid, weightfile, modelfile ):

    worker = PlaneNetworkWorker( context, identity, planeid, gpuid, weightfile, modelfile )
    worker.do_work()

    
class CaffeLArCV1ThreadedWorker( SSNetWorker ):
    """ This worker simply receives data and replies with dummy string. prints shape of array. """

    def __init__( self, identity,broker_ipaddress,
                  gpuid=0, weight_dir="/tmp", model_dir="/tmp", 
                  port=5560, heartbeat_interval_secs=2, num_missing_beats=3,
                  ssh_thru_server=None, print_msg_size=False, reply_in_float16=True ):
        super( CaffeLArCV1ThreadedWorker, self ).__init__(identity,broker_ipaddress,
                                                  port=port, heartbeat_interval_secs=heartbeat_interval_secs, num_missing_beats=num_missing_beats,
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

        
        # Create the threads
        self.workercontext = zmq.Context()

        # create socket to send to the workers
        self.outgoing = self.workercontext.socket(zmq.PUB)
        self.outgoing.sndhwm = 1100000
        self.outgoing.bind( "inproc://worker{}_incoming".format(self._identity) )
        self.syncworkers = self.workercontext.socket(zmq.REP)
        print "inproc://synctomain{}".format(self._identity)        
        self.syncworkers.bind("inproc://synctomain{}".format(self._identity))

        # create sockets from workers
        self.incoming = self.workercontext.socket(zmq.SUB)
        for p in range(self.NPLANES):
            print "CaffeLArCV1ThreadedWorker[{}]: inproc://worker{}_plane{}_outgoing".format(self._identity,self._identity,p)
            self.incoming.connect("inproc://worker{}_plane{}_outgoing".format(self._identity,p))
            self.incoming.setsockopt(zmq.SUBSCRIBE,"plane%d"%(p))            

        # -- worker planes
        print "CaffeLArCV1ThreadedWorker[{}] Create worker threads".format(self._identity)                
        self.plane_processes = []

        for p in range(self.NPLANES):
            #process = multiprocessing.Process(target=start_worker,args=(self.workercontext, self._identity, p, gpuid, self.WEIGHTS[p], self.MODEL_PROTOTXT))
            #process.daemon = True
            #process.start()
            process = PlaneNetworkWorker( self.workercontext, self._identity, p, gpuid, self.WEIGHTS[p], self.MODEL_PROTOTXT )
            process.daemon = True
            print "CaffeLArCV1ThreadedWorker[{}] start worker thread".format(self._identity)                                        
            process.start()
            self.plane_processes.append( process )

        nworkers_ready = 0
        print "CaffeLArCV1ThreadedWorker[{}] Sync with thread workers".format(self._identity)        
        while nworkers_ready<self.NPLANES:
            print "wait for contact from thread worker"
            msg = self.syncworkers.recv()
            print "main thread sends :",msg
            self.syncworkers.send(b'')
            nworkers_ready += 1
        print "CaffeLArCV1ThreadedWorker[{}] Worker Threads Synced. Ready to Go.".format(self._identity)

        
    def process_message(self, frames ):
        """ we expect a batch for each plane 
        """

        # remake arrays
        self.msg_dict = {}
        parts = len(frames)
        for i in range(0,parts,3):
            # parse frames
            name  = frames[i].decode("ascii")
            metamsg  = frames[i+1]
            x_comp = frames[i+2]
            #x_enc  = zlib.decompress(x_comp)

            # decode frames
            
            # -- meta
            meta = decode_larcv1_metamsg( metamsg )
            
            key = (name,meta.plane())
            self.msg_dict[key] = [frames[i],metamsg,x_comp]
                
            print "CaffeLArCV1ThreadedWorker[{}] received array name=\"{}\"  meta={}".format(self._identity,name,meta.dump().strip())

        return "Thanks!"

    def generate_reply(self):
        """
        we run the network
        """
        print "CaffeLArCV1ThreadedWorker[{}] GENERATE REPLY".format(self._identity)
        
        totmsgsize = 0.0
        totcompsize = 0.0
        namelist = []
        # send the images to the workers
        for key,imgmsg in self.msg_dict.items():

            name    = key[0]
            planeid = key[1]

            pubmsg = ["plane%d"%(planeid)]+imgmsg

            print "CaffeLArCV1ThreadedWorker[{}] publish image with name={}".format(self._identity,name)
            self.outgoing.send_multipart( pubmsg )
            namelist.append(name)

        # images have been published
        # pull them from the accumulator

        completed = False
        reply = []
        while len(namelist)>0:

            #print "CaffeLArCV1ThreadedWorker[{}] wait for PUB msg. len(namelist)={}".format(self._identity,len(namelist))
            workermsg = self.incoming.recv_multipart()
            name = workermsg[1].decode("ascii")
            print "CaffeLArCV1ThreadedWorker[{}] collected PUB msg w/ topic={} name={}".format(self._identity,workermsg[0],workermsg[1])

            for frame in workermsg[1:]:
                reply.append( frame )
            namelist.remove( name )

        #print "CaffeLArCV1ThreadedWorker[{}] finished reply for name=\"{}\". size of array portion=%.2f MB (uncompressed %.2f MB)".format(self._identity,name)%(totcompsize/1.0e6,totmsgsize/1.0e6)

        return reply
        
            

if __name__ == "__main__":
    """ test if net loads properly """

    worker = CaffeLArCV1ThreadedWorker(0,"localhost")

    print "press [ENTER] to exit"
    raw_input()

    
