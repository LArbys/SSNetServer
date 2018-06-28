import time
import zmq
from random import randint

from workermessages import PPP_READY, PPP_HEARTBEAT

class SSNetWorker(object):

    def __init__(self,identity,broker_ipaddress, port=5560, heartbeat_interval_secs=2, num_missing_beats=3):
        self._identity = u"Worker-{}".format(identity).encode("ascii")
        self._broker_ipaddress = broker_ipaddress
        self._broker_port = port
        self._heartbeat_interval = heartbeat_interval_secs
        self._num_missing_beats  = num_missing_beats
        self._interval_init      = 1
        self._interval_max       = 32

        self._context = zmq.Context(1)
        self._poller  = zmq.Poller()

        self.connect_to_broker()

    def connect_to_broker(self):
        """ create new socket. connect to server. send READY message """
        self._socket   = self._context.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._poller.register(self._socket,zmq.POLLIN)
        
        self._socket.connect("tcp://%s:%d"%(self._broker_ipaddress,self._broker_port))
        print "SSNetWorker[{}] socket connected".format(self._identity)

        self._socket.send(PPP_READY)
        print "SSNetWorker[{}] sent PPP_READY".format(self._identity)        

    def do_work(self):

        cycles = 0 # for failure sim
        liveness = self._num_missing_beats
        interval = self._interval_init
        heartbeat_at = time.time() + self._heartbeat_interval
        
        while True:

            socks = dict(self._poller.poll(self._heartbeat_interval * 1000))

            # Handle worker activity on backend
            if socks.get(self._socket) == zmq.POLLIN:
                #  Get message
                #  - 3-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = self._socket.recv_multipart()
                if not frames:
                    break # Interrupted
                
                if len(frames) >=3 :
                    # Simulate various problems, after a few cycles
                    cycles += 1
                    if cycles > 3 and randint(0, 5) == 0:
                        print "SSNetWorker[{}] ******* Simulating a crash *******".format(self._identity)
                        break
                    if cycles > 3 and randint(0, 5) == 0:
                        print "SSNetWorker[{}]: ---- Simulating CPU overload ----".format(self._identity)
                        time.sleep(5)
                    print "SSNetWorker[{}]: Replying".format(self._identity)
                    processed = self.process_message( frames[2:] )
                    reply = [frames[0],frames[1]]
                    reply.extend( self.generate_reply() )
                    self._socket.send_multipart(reply)
                    # recieved data from broker. reset liveness count
                    liveness = self._num_missing_beats
                    
                    print "SSNetWorker[{}] doing work.".format(self._identity)
                    time.sleep(1)  # Do some heavy work
                    
                elif len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
                    print "SSNetWorker[{}]: Recieved Queue heartbeat".format(self._identity)
                    # reset liveness count
                    liveness = self._num_missing_beats
                else:
                    print "SSNetWorker[{}]: Invalid message: %s".format(self._identity) % frames
                interval = self._interval_init
            else:
                # poller times out
                liveness -= 1
                if liveness == 0:
                    print "SSNetWorker[{}]: Heartbeat failure, can't reach queue".format(self._identity)
                    print "ssNetWorker[{}]: Reconnecting in %0.2fs..." % interval
                    time.sleep(interval)

                    if interval < INTERVAL_MAX:
                        interval *= 2

                    # reset connection to broker
                    poller.unregister(self._socket)
                    self._socket.setsockopt(zmq.LINGER, 0)
                    self._socket.close()
                    self.connect_to_broker()
                    liveness = self._num_missing_beats

                
            # out of poller if/then
            # is it time to send a heartbeat to the client?
            if time.time() > heartbeat_at:
                print "SSNetWorker[{}]: Worker sending heartbeat".format(self._identity)
                self._socket.send(PPP_HEARTBEAT)
                heartbeat_at = time.time() + self._heartbeat_interval                
            

        # end of while loop

        return True

    def process_message(self,frames):
        raise NotImplemented("Inherited classes must define this function")

    def generate_reply(self):
        raise NotImplemented("Inherited classes must define this function")
