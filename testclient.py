import time
import zmq
from collections import OrderedDict
from client import SSNetClient

class TestClient(SSNetClient):

    def __init__( self, *args, **kwargs ):
        super( TestClient,self).__init__(*args,**kwargs)

    def get_batch( self ):
        # no batch
        return

    def make_outgoing_message( self ):
        return b'Hello from TestClient[{}]'.format(self._identity)

    def process_reply(self,frames):
        print "TestClient[{}] received: \"{}\"".format( self._identity, frames[0] )
        return
    
