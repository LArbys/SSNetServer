import time
from random import randint
from worker import SSNetWorker

class TestWorker(SSNetWorker):

    def __init__(self, *args, **kwargs):
        super( TestWorker, self ).__init__( *args, **kwargs )
        self.cycles = 0
        
    def process_message(self,frames):
        # Simulate various problems, after a few cycles
        self.cycles += 1
        if self.cycles > 3 and randint(0, 5) == 0:
            print "TestWorker[{}] ******* Simulating a crash *******".format(self._identity)
            raise RuntimeError("simulated crash")
        if self.cycles > 3 and randint(0, 5) == 0:
            print "TestWorker[{}]: ---- Simulating CPU overload ----".format(self._identity)
            time.sleep(5)


    def generate_reply(self):
        reply = [b'hello from TestWorker[{}]'.format(self._identity)]
        return reply        
        
