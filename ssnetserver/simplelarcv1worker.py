from worker import SSNetWorker
import numpy as np

import msgpack
import msgpack_numpy as m
m.patch()

class SimpleLArCV1Worker( SSNetWorker ):

    def __init__( self, identity,broker_ipaddress, port=5560, heartbeat_interval_secs=2, num_missing_beats=3):
        super( SimpleLArCV1Worker, self ).__init__(identity,broker_ipaddress, port=port, heartbeat_interval_secs=heartbeat_interval_secs, num_missing_beats=num_missing_beats)

    def process_message(self, frames ):

        # remake arrays
        parts = len(frames)
        for i in range(0,parts,2):
            name  = frames[i].decode("ascii")
            x_enc = frames[i+1]

            arr = msgpack.unpackb(x_enc, object_hook=m.decode)

            print "SimpleLArCVWorker[{}] received array name=\"{}\" shape={}".format(self._identity,name,arr.shape)

        return "Thanks!"
            
