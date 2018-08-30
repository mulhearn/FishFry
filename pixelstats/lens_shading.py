#!/usr/bin/env python

import sys
from unpack import *
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import argparse

from geometry import *

FILE_NAME = "calib/lens.npz"

def calculate(args):

    # load the image geometry:
    try:
        geom = np.load("calib/geometry.npz");
    except:
        print "calib/geometry.npz does not exist.  Use dump_header.py --geometry"
        return
    width  = geom["width"]
    height = geom["height"]
    index  = np.arange(width*height,dtype=int)
    xpos = index % width
    ypos = index / width

    # load the pixel gains:
    try:
        filename = "calib/gain.npz"
        gains  = np.load(filename);
    except:
        print "could not process file ", filename, " as .npz file.  Run gain.py with --commit option first?"
        return
    gain       = gains['gain']
    intercept  = gains['intercept']

    # load the hot cell list:
    try:
        filename = "calib/hot.npz"
        hots  = np.load(filename);
    except:
        print "could not process file ", filename, " as .npz file.  Run gain.py with --commit option first?"
        return
    hot       = hots['hot_list']

    # TODO: omit dark pixels, if present:
    good = np.isfinite(gain) & np.isfinite(intercept) 
    normal = good

    # position for down sampling by 8x8 
    ds = args.down_sample
    down, nx, ny = down_sample(width, height, ds, ds)
    G = np.zeros(nx*ny, dtype=float)
    S = np.zeros(nx*ny, dtype=float)
    W = np.zeros(nx*ny, dtype=float)
    for i in np.where(normal)[0]:
        if (args.short & (i > 100000)):
            break;
        if (gain[i] < 0):
            continue
        G[down[i]] += gain[i]
        S[down[i]] += 1.0
    nz = np.nonzero(S)[0]
    G[nz] = G[nz]/S[nz]
    # map back to full resolution:
    avg_gain = np.array([G[down[i]] for i in range(width*height)])
    lens = G.reshape(ny,nx)

    np.savez(FILE_NAME, down_sample=ds, avg_gain=avg_gain, lens=lens)

    return lens

def load(args):    
    try:
        lens = np.load(FILE_NAME);
    except:
        print "calib/lens.npz does not exist.  Run without --plot_only first?";
        return
    lens  = lens["lens"]
    return lens

def plot(args, lens):
    plt.imshow(lens, vmin=args.min_gain, vmax=args.max_gain)
    plt.colorbar()
    plt.show()

def analysis(args):
    if (args.plot_only):
        lens = load(args)
    else:    
        lens = calculate(args)

    plot(args,lens)

        
if __name__ == "__main__":
    example_text = '''examples:

    ...'''
    
    parser = argparse.ArgumentParser(description='construct the lens shading map from calculated gains', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sandbox',action="store_true", help="run sandbox code and exit (for development).")
    parser.add_argument('--dark',action="store_true", help="exclude dark pixels from analysis.")
    parser.add_argument('--short',action="store_true", help="short (test) analysis of a few pixels.")
    parser.add_argument('--down_sample',  type=int, default=8,help="down sampling amount.")
    parser.add_argument('--max_gain',  type=float, default=10,help="minimum gain for plot.")
    parser.add_argument('--min_gain',  type=float, default=0,help="maximum gain for plot.")
    parser.add_argument('--plot_only',action="store_true", help="load and plot previous results.")
    args = parser.parse_args()
    analysis(args)



