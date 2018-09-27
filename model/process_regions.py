#! /usr/bin/env python

import sys
import argparse
import datetime

import numpy as np
import matplotlib.pyplot as plt

from unpack import *

dep_coll = np.array([], dtype=float)
slab_coll      = np.array([], dtype=float)
sum_coll     = np.array([], dtype=float)

def process(filename,args):
    global dep_coll, slab_coll, sum_coll
    
    header,depletion,slab,region= unpack_all(filename)

    num_region = region.shape[0]

    if (args.txtdump):
        count = 0
        for i in range(num_region):
            print "region:       ", region[i]
            count += 1

        print "total number of regions:  ", num_region
        return


    sum = np.array([np.sum(region[i]) for i in range(num_region)])

    sum_coll = np.append(sum_coll, sum)
    dep_coll = np.append(dep_coll, depletion)
    slab_coll = np.append(slab_coll, slab)


def analysis(args):
    global sum_coll, dep_coll, slab_coll

    num = dep_coll.size
    sum_coll = sum_coll.reshape((num,-1))

    np.savez(args.out, depletion_width=dep_coll, slab_depth=slab_coll, sum=sum_coll)

    for i in range(num):
        h,bins = np.histogram(np.clip(sum_coll[i],0,500), bins=500, range=(0,500))
        err = h**0.5
        cbins = 0.5*(bins[:-1] + bins[1:])
        plt.errorbar(cbins,h,yerr=err,fmt="o")
    plt.show()
        

    
if __name__ == "__main__":

    example_text = ""
    
    parser = argparse.ArgumentParser(description='Combine multiple pixelstats data files.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', metavar='FILE', nargs='+', help='file to process')
    parser.add_argument('--txtdump',action="store_true", help="dump regions to screen")
    parser.add_argument('--out',metavar="FILE", help="output to filename FILE",default="model.npz")  
    args = parser.parse_args()

    for filename in args.files:
        print "processing file:  ", filename
        process(filename, args)

    analysis(args)
