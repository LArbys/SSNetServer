# SSNet Server

A client-worker proxy using ZMQ to server SSNet predictions on the Tufts Cluster

The code is a copy of the paranoid pirate proxy from the ZeroMQ Guide

There are two goals:

* Create a production network where many clients read data event-by-event, send to a collection of workers, receive net output, and write to disk
* Create a training network where single client app asks workers for batch data

## Classes

### SSNetWorker/SSNetClient

These are base classes that are meant to handle the network portion of the code.
They are to be inherited by child classes that handle either the reading/writing of data or the processing through a network.

Note that child client and workers are meant to be implemented together so that they understand their messages.
We do not enforce a standard messaging protocol.
This is meant to reflect the fact that different tasks usually differ in the details of the input/output data required.
Though similar, I am not smart enough to define generic behavior.

### SSNetBroker

This class is the proxy between clients and workers.
It need not know anything about the data it is passing.
It's only job is to balance the load and keep track of connected workers (through heartbeats).

### SimpleLArCV1Client

This is a very basic client that reads larcv1 event images and sends it out to the SSNetBroker.
It only handles Image2D objects for now.
You can provide it a list of producer names via the `product_dict` argument of the constructor.
It will prepare a numpy array for each image product given.  The array shapes are

    (batchsize, number of images in event container, height, width)

The message sent to the worker is:

    [frame 0] "producer name" (string)
    [frame 1] numpy array for batch
    [frame 2] "producer name" (string)
    [frame 3] numpy array for batch
    (and so on...)

The received message is expected in the same format

    [frame 0] "returned array name" (string)
    [frame 1] numpy array
    ...

The arrays in the received messages will be saved to an output larcv file.

### DummyLArCV1Worker

Used for debugging.  Expects message from SimpleLArCV1Client and dumps numpy array shapes to standard out.
Returns:

    [frame 0] "dummy"
    [frame 1] (1,1,1,1) numpy array