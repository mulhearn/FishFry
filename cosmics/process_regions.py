#! /usr/bin/env python

# dump a header from run data

import sys
import argparse
import datetime

from unpack_trigger import *
from calibrate import *
from maximum import *

region_coll    = np.array([], dtype=int)
timestamp_coll = np.array([], dtype=float)
delta_coll     = np.array([], dtype=float)
px_coll        = np.array([], dtype=int)
py_coll        = np.array([], dtype=int)
shape          = None
total_exposure = 0

def process(filename,args):
    global region_coll, timestamp_coll, delta_coll, px_coll, py_coll,shape,total_exposure
    header,px,py,highest,region,nanostamp,millistamp,images,dropped = unpack_all(filename)
    width = interpret_header(header,"width")
    dx = interpret_header(header,"region_dx")
    dy = interpret_header(header,"region_dy")
    threshold,prescale = get_trigger(header)


    exposure  = interpret_header(header, "exposure")
    total_exposure += images*(exposure*1E-9);

    timestamp = millistamp*1E-3


    if (shape == None):
        shape = region.shape

    if (args.framerate):
        tmin     = np.min(millistamp)
        tmax     = np.max(millistamp)
        elapsed  = (tmax - tmin)*1E-3
        exposure = interpret_header(header, "exposure")*1E-9
        if (images > 0):
            duration = elapsed / images
        else:
            duration = 0
        dead     = (duration - exposure) / duration

        print "images:              ", images
        print "first image:         ", tmin, " -> ", datetime.datetime.fromtimestamp(tmin*1E-3)    
        print "last image:          ", tmax, " -> ", datetime.datetime.fromtimestamp(tmax*1E-3)     
        print "interval (s):        ", elapsed  
        print "frame duration (s):  ", duration
        print "exposure (s):        ", exposure
        print "deadtime frac:       ", dead
        return


    num_region = region.shape[0]
    keep = np.full((num_region),True,dtype=bool)

    if (args.no_hot):
        try:
            filename = "calib/hot.npz"
            hots  = np.load(filename);
        except:
            print "could not process file ", filename, " as .npz file."
            return        
        hot_list = hots['hot']        
        index = py*width + px
        hot = np.in1d(index, hot_list)
        keep = keep & (hot == False)

    if (args.calib):
        region = calibrate_region(px,py,region,dx,dy)

    if (args.max):
        lmax = local_maximum(region, dx, dy)
        keep = keep & lmax

    if (args.highest):
        keep = keep & (highest == threshold.size)

    if (args.zerobias):
        keep = keep & (highest == 0)

    if (args.no_zerobias):
        keep = keep & (highest > 0)

    px      = px[keep]
    py      = py[keep]
    timestamp    = timestamp[keep]
    region  = region[keep,:]
    num_region = region.shape[0]

    if (args.hodo or args.tagged):
        tagfile = "tags.npz"
        try:
            hnpz = np.load(tagfile)
        except:
            print "could not process file ", tagfile, " as .npz file."
            exit(0)
        a = hnpz['chan_a']
        b = hnpz['chan_b']
        c = hnpz['chan_c']
        ab  = np.intersect1d(a,b)
        imin = np.array([(np.abs(ab-timestamp[i])).argmin() for i in range(timestamp.size)])
        delta = timestamp - ab[imin]
        if (args.tagged):            
            keep = (np.abs(delta) < 1.0)
            print "keeping only ", np.sum(keep), " muon tagged regions of ", keep.size
            delta   = delta[keep]
            px      = px[keep]
            py      = py[keep]
            timestamp    = timestamp[keep]
            region  = region[keep,:]
            num_region = region.shape[0]            
    else:
        delta = None


    if (args.single):
        unq = np.unique(timestamp)
        print "found ", unq.size, " unique timestamps of ", timestamp.size
        # find indices (imax) of regions with the largest sum amongst all regions sharing the same timestamp:
        map  = [[ j for j in np.where(timestamp == unq[i])[0]] for i in range(unq.size)] 
        smax  = [np.argmax(np.sum(region[map[k],:])) for k in range(unq.size)]
        imax = [map[i][smax[i]] for i in range(unq.size)]        
        px      = px[imax]
        py      = py[imax]
        timestamp    = timestamp[imax]
        region  = region[imax,:]
        num_region = region.shape[0]
        if (delta != None):
            delta = delta[imax]

    if (args.txtdump):
        count = 0
        for i in range(num_region):
            print "timestamp:    ", timestamp[i]
            if (delta != None):
                print "delta:        ", delta[i]
            print "px:           ", px[i]
            print "py:           ", py[i]
            print "highest:      ", highest[i]
            print "region:       ", region[i]
            count += 1

        print "images:                   ", images
        print "total number of regions:  ", num_region
        print "regions shown:            ", count
        print "total dropped triggers:   ", dropped
        return

    region_coll    = np.append(region_coll, region)
    timestamp_coll = np.append(timestamp_coll, timestamp)
    if (delta != None):
        delta_coll     = np.append(delta_coll,delta)
    px_coll = np.append(px_coll, px)
    py_coll = np.append(py_coll, py)


def analysis(args):
    global region_coll, timestamp_coll, delta_coll, px_coll, py_coll,shape,total_exposure

    # reshape the region collection after appending as 1-d array:
    region_coll = region_coll.reshape((-1,shape[1]))

    #print "new region shape:  ", region_coll.shape

    print "saving ", total_exposure, " seconds of exposure to file ", args.out

    np.savez(args.out, region=region_coll, timestamp=timestamp_coll, delta=delta_coll, px=px_coll, py=py_coll,total_exposure=total_exposure)    
    
if __name__ == "__main__":

    example_text = ""
    
    parser = argparse.ArgumentParser(description='Combine multiple pixelstats data files.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', metavar='FILE', nargs='+', help='file to process')

    parser.add_argument('--calib',action="store_true", help="apply calibrated weights to region data")
    parser.add_argument('--framerate',action="store_true", help="calculate framerate and exit")
    parser.add_argument('--txtdump',action="store_true", help="calculate framerate and exit")

    parser.add_argument('--hodo',action="store_true", help="include nearest muon hodoscope tag")
    parser.add_argument('--single',action="store_true", help="save only one region from each timestamp")

    parser.add_argument('--max',action="store_true", help="dump only regions centered on maximum value")
    parser.add_argument('--zerobias',action="store_true", help="dump only regions from zerobias")
    parser.add_argument('--no_zerobias',action="store_true", help="drop zerobias regions")
    parser.add_argument('--highest',action="store_true", help="dump only regions passing unprescaled threshold")
    parser.add_argument('--no_hot',action="store_true", help="drop regions centered on a hot pixel")
    parser.add_argument('--out',metavar="FILE", help="output to filename FILE",default="regions.npz")  
    parser.add_argument('--tagged',action="store_true", help="dump only regions near a hodoscope tag in time")
    args = parser.parse_args()

    for filename in args.files:
        print "processing file:  ", filename
        process(filename, args)

    analysis(args)
