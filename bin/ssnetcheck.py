#!/usr/bin/env python

import os,sys
from larcv import larcv
import numpy as np

supera_file = sys.argv[1]
ssnet_file  = sys.argv[2]
tagger_file = sys.argv[3]

io = larcv.IOManager( larcv.IOManager.kREAD )
io.add_in_file( supera_file )
io.add_in_file( ssnet_file )
io.add_in_file( tagger_file )
io.initialize()

nentries = io.get_n_entries()
NBAD = 0
for ientry in xrange(nentries):

    io.read_entry(ientry)
    print "[ENTRY %d]"%(ientry)
        
    adc_v = io.get_data(larcv.kProductImage2D,"wire").Image2DArray()
    shower_v = [ io.get_data(larcv.kProductImage2D,"uburn_plane%d"%(p)).Image2DArray() for p in range(3) ]

    croi_v = io.get_data(larcv.kProductROI,"croi").ROIArray()
    ncroi = croi_v.size()

    nimgs = [ shower_v[p].size() for p in range(3) ]
    if 0 in nimgs and ncroi>0:
        print "  No shower images were made when there was a CROI."
        NBAD+=1
        continue
    elif 0 in nimgs and ncroi==0:
        print "  No CROI to run SSNet on."
        continue

    # crop same region
    adc_crop_v = [ adc_v.at(p).crop( shower_v[p].at(0).meta() ) for p in range(3) ]

    # now compare overlap
    for p in xrange(3):
        adc_crop     = larcv.as_ndarray( adc_crop_v[p] )
        ssnet_shower = larcv.as_ndarray( shower_v[p].at(0) )

        # binary shower image
        ssnet_shower[ ssnet_shower>0  ] = 1.0
        nshowerpix = np.sum(ssnet_shower)

        # maks out places with sub adc threshold
        ssnet_shower[ adc_crop<10 ] = 0.0
        nabovethresh = np.sum( ssnet_shower )

        # binary adc crop
        adc_crop[ adc_crop<10 ] = 0.0
        adc_crop[ adc_crop>0 ] = 1.0
        nadcthresh = np.sum( adc_crop )
        nadczero   = np.sum( adc_crop==0.0 )


        print "  (plane ",p,"): Number of pixels above ADC threshold: ",nadcthresh," number-zero=",nadczero
        print "  (plane ",p,"): Number of shower pixels: ",nshowerpix
        print "  (plane ",p,"): Number of ssnet pixels with score and above threshold: ",nabovethresh
        if nshowerpix>0:
            frac_w_charge = float(nabovethresh)/float(nshowerpix)
            print "  (plane ",p,") fraction ssnet pixles above threshold: ",frac_w_charge
            if frac_w_charge<0.95:
                NBAD += 1
                
print "Number of bad images: "
print NBAD
        
        

