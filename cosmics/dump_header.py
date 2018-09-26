#! /usr/bin/env python

# dump a header from run data

import sys
import argparse
import numpy as np

def process(filename,args):
    if (args.hist):
        import unpack_hist as unpack
    else:
        import unpack_trigger as unpack

    header = unpack.unpack_header(filename)
    unpack.show_header(header)

    if (args.geometry):
        width = unpack.interpret_header(header,"width")
        height = unpack.interpret_header(header,"height")
        print "recording width:   ", width
        print "recording height:  ", height
        np.savez("calib/geometry.npz", width=width, height=height)

    if (args.region):
        width = unpack.interpret_header(header,"width")
        height = unpack.interpret_header(header,"height")
        dx = unpack.interpret_header(header,"region_dx")
        dy = unpack.interpret_header(header,"region_dy")
        center_index = dx + dy + 2*dx*dy
        print "recording width:         ", width
        print "recording height:        ", height
        print "recording dx:            ", dx
        print "recording dy:            ", dy
        print "recording center index:  ", center_index
        np.savez("calib/region.npz", width=width, height=height,dx=dx,dy=dy,center_index=center_index)
    
if __name__ == "__main__":

    example_text = '''examples:

    ./dump_header.py data/FishStand/run_*_part_0_pixelstats.dat
    ./dump_header.py --geometry data/FishStand/run_*_part_0_pixelstats.dat'''
    
    parser = argparse.ArgumentParser(description='Combine multiple pixelstats data files.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', metavar='FILE', nargs='+', help='file to process')
    parser.add_argument('--hist',action="store_true", help="dump header from a cosmic histogram file")
    parser.add_argument('--geometry',action="store_true", help="save image geometry data to calibration file")
    parser.add_argument('--region',action="store_true", help="save region data to calibration file")

    args = parser.parse_args()

    if (args.geometry):
        if (len(args.files) != 1):
            print "specify only one file for defining the image geometry\n"
            exit(0)
    if (args.region):
        if (len(args.files) != 1):
            print "specify only one file for defining the region geometry\n"
            exit(0)
        if (args.hist):
            print "use a trigger file for defining the region geometry\n"
            exit(0)

    for filename in args.files:
        print "processing file:  ", filename
        process(filename, args)

        
