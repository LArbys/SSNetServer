from worker import SSNetWorker
import numpy as np

import msgpack
import msgpack_numpy as m
m.patch()


class DummyLArCV1Worker( SSNetWorker ):
    """ This worker simply receives data and replies with dummy string. prints shape of array. """

    def __init__( self, identity,broker_ipaddress, port=5560, heartbeat_interval_secs=2, num_missing_beats=3):
        super( DummyLArCV1Worker, self ).__init__(identity,broker_ipaddress, port=port, heartbeat_interval_secs=heartbeat_interval_secs, num_missing_beats=num_missing_beats)
        self.shape_dict = {}
        
    def process_message(self, frames ):

        # remake arrays
        self.shape_dict = None
        parts = len(frames)
        for i in range(0,parts,2):
            name  = frames[i].decode("ascii")
            x_enc = frames[i+1]

            arr = msgpack.unpackb(x_enc, object_hook=m.decode)
            if self.shape_dict is None:
                self.shape_dict = {}
                self.shape_dict[ "dummy" ] = arr.shape
                
            print "DummyLArCVWorker[{}] received array name=\"{}\" shape={}".format(self._identity,name,arr.shape)

        return "Thanks!"

    def generate_reply(self):
        reply = []
        for name,shape in self.shape_dict.items():
            reply.append( name )
            dummy = np.zeros( shape, dtype=np.float32 )            
            x_enc = msgpack.packb( dummy, default=m.encode )
            reply.append(x_enc)

        return reply
        
            
