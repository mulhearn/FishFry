#!/usr/bin/env python

import sys
import argparse
import re

import numpy as np
import matplotlib.pyplot as plt
import unpack_hist as hist
import unpack_trigger as trigger

from calibrate import *
from plotting import mark_plot

ref_images = 0;
ref_hist = None;

trig_images = None;
trig_hist   = [];
trig_label  = []; 

total_exposure = 0

def process_hist(filename, args):
    global ref_images, ref_hist
    # load data:
    header,hist_uncal,hist_nohot,hist_calib = hist.unpack_all(filename)
    images = hist.interpret_header(header, "images")
    hist_prescale = hist.interpret_header(header, "hist_prescale")

    ref_images += images / hist_prescale

    #width  = hist.interpret_header(header, "width")
    #height = hist.interpret_header(header, "height")

    if (args.calib):
        add_hist = hist_calib.astype(float)
    else:
        add_hist = hist_nohot.astype(float)

    if (ref_hist == None):
        ref_hist = add_hist.astype(float)
    else:
        ref_hist = ref_hist + add_hist.astype(float)


def process_trig(filename,args):
    global trig_images, trig_hist, total_exposure
    header,px,py,highest,region,timestamp,millistamp,images,dropped = trigger.unpack_all(filename)
    num_zerobias = trigger.interpret_header(header, "num_zerobias")
    dx = trigger.interpret_header(header,"region_dx")
    dy = trigger.interpret_header(header,"region_dy")
    center_index = dx + dy + 2*dx*dy
    exposure = trigger.interpret_header(header,"exposure") * 1E-9
    total_exposure += exposure * images

    threshold,prescale = trigger.get_trigger(header)

    region_calib = calibrate_region(px,py,region,dx,dy)
    if (args.calib):
        region = region_calib
    else:
        region = calibrate_region(px,py,region,dx,dy,remove_hot_only=True)

    # allocate number of prescales plus one (for zerobias) prescaled image counts:
    if (trig_images == None):
        trig_images = np.zeros(prescale.size+1, dtype=float)
        print "thresholds:  ", threshold
        print "prescales:   ", prescale
        
    if (len(trig_hist) == 0):
        for i in range(prescale.size+1):
            trig_hist.append(np.zeros(args.max, dtype=float))

    if (len(trig_label) == 0):
        trig_label.append("zero-bias")
        for i in range(prescale.size):
            trig_label.append("prescale " + str(prescale[i]))

    # select zero-bias events not included in the trigger sample (calibrated value below lowest threshold)
    untrig_zerobias = (region_calib[:,center_index] < threshold[0])    
    h,bins = np.histogram(np.clip(region[untrig_zerobias,center_index],0,args.max), bins=args.max, range=(0,args.max))
    trig_images[0] += images*float(num_zerobias)/(5328*3000)
    trig_hist[0] = trig_hist[0]+h
    
    for i in range(prescale.size):
        trig_images[i+1] += float(images) / prescale[i]
        trig = region[(highest==(i+1)),center_index]
        h,bins = np.histogram(trig, bins=args.max, range=(0,args.max))
        trig_hist[i+1] = trig_hist[i+1]+h.astype(float)
    return

def analysis(args):
    global ref_hist, ref_images
    bins = np.arange(0,args.max)+0.5
    ref_hist = ref_hist[:args.max]
    ref_hist = ref_hist / ref_images

    if (args.combine):
        combined = np.zeros(args.max, dtype=float)
        for i in range(trig_images.size):
            combined = combined + trig_hist[i]/ trig_images[i]
        plt.plot(bins,combined,"o", label="scaled data")        
        plt.plot(bins,ref_hist,"r-", label="monitoring histogram")
    else:
        plt.plot(bins,ref_hist,"r--", label="monitoring histogram")
        for i in range(trig_images.size):
            err = trig_hist[i]**0.5
            trig_hist[i] = trig_hist[i]/ trig_images[i]
            err = err / trig_images[i]
            plt.errorbar(bins,trig_hist[i],yerr=err,fmt="o", label=trig_label[i])        
        plt.plot(bins,ref_hist,"r--")

    plt.yscale('log')
    plt.xlabel("pixel value")
    plt.ylabel("rate per image")
    plt.ylim(1E-5,1E9)
    plt.legend(numpoints=1)
    mark_plot(0.1,1E-1,"exposure:  " + str(total_exposure) + " s")
    if (args.calib):
        mark_plot(0.1,1E-2,"calibrated pixels")
        plt.xlabel("pixel value [electrons]")
    else:
        mark_plot(0.1,1E-2,"uncalibrated pixels")
        plt.xlabel("pixel value [DN]")


    name = "plots/rate"
    if (args.calib):
        name = name + "_calib"
    else: 
        name = name + "_uncalib"
    if (args.combine):
        name = name + "_combined"
    name = name + "_max_" + str(args.max) + ".pdf"
    plt.savefig(name)


    plt.show()

    
if __name__ == "__main__":
    example_text = '''examples:

    ...'''
    
    parser = argparse.ArgumentParser(description='Plot rate from Cosmics.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='+', metavar="FILE", help='histogram and/or trigger file(s) to processs')
    parser.add_argument('--sandbox',action="store_true", help="run sandbox code and exit (for development).")
    parser.add_argument('--calib',action="store_true", help="compare calibrated pixel values.")
    parser.add_argument('--max',  type=int, default=100,help="maximum pixel value in rate plot (x-axis).")
    parser.add_argument('--combine',action="store_true", help="combine data weighted by prescale factors.")
    args = parser.parse_args()


    hist_re = re.compile(r".*_hist.*")    
    for file in args.files:        
        match = hist_re.match(file)
        if (match != None):
            print "processing histogram file:  ", file
            process_hist(file, args)
        else:
            print "processing trigger file:    ", file
            process_trig(file, args)

    analysis(args)
    

