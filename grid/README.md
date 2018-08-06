# Instructions on how to start the SSNet server

To set up the SSNet server, we need to

* start the server/proxy
* start up some workers at various locations
* launch the clients (PUBs project and not covered here)

On the Tufts cluster, the code is in the following PUBS directory

     /cluster/tufts/wongjiradlab/larbys/pubs/dlleepubs/serverssnet

## Setup the server/proxy (on the Tufts cluster)

Go to the PUBS directory for `ssnetserver` scripts

    cd /cluster/tufts/wongjiradlab/larbys/pubs/dlleepubs/serverssnet

Make sure that the server is not running

    squeue | grep ssn_serv

If a server is already running, you'll see something like

```
[twongj01@login001 serverssnet]$ squeue | grep ssn_serv
32870754       gpu ssn_serv twongj01  R      23:10      1 pgpu03
```

If running, DO NOT start another server without stopping the current one.

If no longer running, first delete the file containing the timestamp of when the last broker started.

    rm ssnetserver_broker_start.txt

Now you can start the server
   
    sbatch submit_broker.sh

## Setting up workers

### Tufts

Go to the PUBS `ssnetsever` directory

    cd /cluster/tufts/wongjiradlab/larbys/pubs/dlleepubs/serverssnet

Note, you only have to run `prep_pgpu03_workers.sh` once after a long time. (But it's not a long job.)

    sbatch prep_pgpu03_workers.sh

Then you should be able to run the workers using

    sbatch submit_worker_pgpu03.sh

Some important options:

```
#SBATCH --array=0-16
```
This tells us to create workers 0-16, inclusive. This is the max.  

Sometimes workers do not start. So you'll have to launch specific workers again. Use this `array` variable to specify specific workers.

To see which workers are running, you can use

```
[twongj01@login001 serverssnet]$ squeue | grep ssn_work
32870765_2       gpu ssn_work twongj01  R      11:42      1 pgpu03
32870765_3       gpu ssn_work twongj01  R      11:42      1 pgpu03
32870765_4       gpu ssn_work twongj01  R      11:42      1 pgpu03
```

The workers with ID of 2,3,4 are running in the above example.

### Meitner

### Davis (Michigan)

### Nevis