#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt

import argparse
import datetime

def mark_exposure(total_exposure):
    0, ymax = plt.ylim()
data_width = xmax - x0
data_height = ymax - y0
plt.text(x0 + data_width * 1.5, y0 + data_height * 0.5, 'Some text')
    


def process(hfile, pfile, args):
    try:
        hnpz = np.load(hfile)
    except:
        print "could not process file ", hfile, " as .npz file."
        return

    try:
        pnpz = np.load(pfile)
    except:
        print "could not process file ", pfile, " as .npz file."
        return

    a = hnpz['chan_a']
    b = hnpz['chan_b']
    c = hnpz['chan_c']

    ab  = np.intersect1d(a,b)
    print "ab:   ", ab.size

    print ab

    p = pnpz['time']
    total_exposure = pnpz['total_exposure']
    print p
    
    print "phone candidates:  ", p.size
    print "hodoscope muons:   ", ab.size


    pstart = np.min(p)
    pend   = np.max(p)

    print "phone times start at ", datetime.datetime.fromtimestamp(pstart)
    print "hodoscope times start at ", datetime.datetime.fromtimestamp(np.min(ab))
    print "phone times end at ", datetime.datetime.fromtimestamp(pend)
    print "hodoscope times end at ", datetime.datetime.fromtimestamp(np.max(ab))


    imin = np.array([(np.abs(ab-p[i])).argmin() for i in range(p.size)])
    delta = p - ab[imin]

    np.savez("chase.npz", delta=delta)

    nbins = 121

    if (args.comb):
        print "simulating combinatoric background."
        ngen = 100000
        ncbins = 101
        comb = pstart + np.random.uniform(0,1.0,ngen)*(pend - pstart)
        imin = np.array([(np.abs(ab-comb[i])).argmin() for i in range(comb.size)])
        dcomb = comb - ab[imin]
        print dcomb[0:5]
        hc,bins = np.histogram(dcomb, bins=ncbins, range=(-60,60))
        hc = hc.astype(float) * p.size / ngen * ncbins / nbins
        cbins = 0.5*(bins[:-1] + bins[1:])
        plt.plot(cbins,hc,"r-",label="combinatorics")


    h,bins = np.histogram(int(delta), bins=121, range=(-60,60))
    err = h**0.5
    cbins = 0.5*(bins[:-1] + bins[1:])
    plt.errorbar(cbins,h,yerr=err,color="black",fmt="o",label="phone")
    plt.ylabel("phone images")
    plt.xlabel("delta t [s]")
    plt.title("Time difference between smartphone and muon hodoscope")
    
    s = "exposure " + str(total_exposure) + " s" 
    plt.text(20, 35, s)
    plt.legend(numpoints=1)
    plt.savefig("plots/muon.pdf")
    plt.show()

    print "total exposure:  ", total_exposure

    




    
if __name__ == "__main__":
    example_text = '''examples:

    ./calibrate_time.py raw.npz'''
    
    parser = argparse.ArgumentParser(description='Compre timestamps between phone and hodoscope.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('hfile', metavar='HFILE', help='hodoscope npz file')
    parser.add_argument('pfile', metavar='PFILE', help='phone npz file')
    parser.add_argument('--sandbox',action="store_true", help="run sandbox code and exit (for development).")
    parser.add_argument('--comb',action="store_true", help="simulate the combinatorics background.")
    args = parser.parse_args()

    process(args.hfile, args.pfile, args)




