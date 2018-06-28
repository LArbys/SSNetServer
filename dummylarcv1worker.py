from worker import SSNetWorker
import numpy as np

import msgpack
import msgpack_numpy as m
m.patch()

from workermessages import decode_larcv1_metamsg


class DummyLArCV1Worker( SSNetWorker ):
    """ This worker simply receives data and replies with dummy string. prints shape of array. """

    def __init__( self, identity,broker_ipaddress, port=5560, heartbeat_interval_secs=2, num_missing_beats=3):
        super( DummyLArCV1Worker, self ).__init__(identity,broker_ipaddress, port=port, heartbeat_interval_secs=heartbeat_interval_secs, num_missing_beats=num_missing_beats)
        self.shape_dict = {}
        
    def process_message(self, frames ):

        # remake arrays
        self.shape_dict = None
        self.meta_dict  = None
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
            if self.shape_dict is None:
                self.shape_dict = {}
                self.shape_dict[ "dummy" ] = arr.shape
            if self.meta_dict is None:
                self.meta_dict = {}
                self.meta_dict[ "dummy" ] = meta
                
            print "DummyLArCVWorker[{}] received array name=\"{}\" shape={} meta={}".format(self._identity,name,arr.shape,meta.dump().strip())

        return "Thanks!"

    def generate_reply(self):
        reply = []
        for name,shape in self.shape_dict.items():

            dummy = np.zeros( shape, dtype=np.float32 )
            meta  = self.meta_dict[name]
            x_enc = msgpack.packb( dummy, default=m.encode )

            reply.append( name )
            reply.append( meta.dump().strip() )
            reply.append(x_enc)

        return reply
        
            
