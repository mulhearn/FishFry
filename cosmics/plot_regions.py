#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors


import argparse

width = 0
height = 0
dx = 0
dy = 0
center_index = 0

def _draw_regions(cand,num,tag):
        x = range(0,2*dx+2,1)
        y = range(0,2*dy+2,1)
        X, Y = np.meshgrid(x, y)
                
        done = False
        j=0
        count=0
        while(not done):
            f, axes = plt.subplots(5, 5, sharex='col', sharey='row')
            axes = axes.flatten()        
            for i in range(25):
                print "debug:  ", i, j
                if (j<num):
                    im = axes[i].pcolormesh(X, Y, cand[j,:,:],cmap='coolwarm', vmin=0, vmax=200)
                    axes[i].set_xticks([0.5,2.5,4.5])
                    axes[i].set_xticklabels(["-2","0","2"])
                    axes[i].set_yticks([0.5,2.5,4.5])
                    axes[i].set_yticklabels(["-2","0","2"])
                    print cand[j,:,:]
                else:
                    im = axes[i].pcolormesh(X, Y, 0*cand[0,:,:],cmap='coolwarm', vmin=0, vmax=200)
                    axes[i].set_xticks([0.5,2.5,4.5])
                    axes[i].set_xticklabels(["-2","0","2"])
                    axes[i].set_yticks([0.5,2.5,4.5])
                    axes[i].set_yticklabels(["-2","0","2"])
                axes[22].set_xlabel("x position")
                axes[10].set_ylabel("y position")
                if (tag):
                    axes[2].set_title("tagged muon candidates.")
                else:
                    axes[2].set_title("anti-tagged muon candidates.")
                j = j + 1
            if (j>=num):
                done = True;
            f.subplots_adjust(right=0.8,hspace=0.1,wspace=0.1)
            cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
            f.colorbar(im, cax=cbar_ax)
            if (tag):
                plt.savefig("plots/tagged_muons_"+str(count)+".pdf")
            else:
                plt.savefig("plots/antitagged_muons_"+str(count)+".pdf")
            count += 1
            plt.show()

def init(args):
    global width,height,dx, dy, center_index
    try:
        region = np.load("calib/region.npz");
    except:
        print "calib/region.npz does not exist.  Use dump_header.py --region"
        return
    width        =  region['width'] 
    height       =  region['height']
    dx           =  region['dx'] 
    dy           =  region['dy'] 
    center_index =  region['center_index'] 
    print "dx:            ", dx
    print "dy:            ", dy
    print "center index:  ", center_index

def mark_plot(fx, fy, s):
    ydn,yup = plt.ylim()
    xdn,xup = plt.xlim()
    posx = xdn + (xup-xdn) * fx
    posy = ydn + (yup-ydn) * fy
    plt.text(posx, posy, s,size=14)
    
    
def process(filename, args):
    plot_delta       = True
    plot_delta_fail  = True
    plot_sum         = True
    plot_pos         = True
    draw_tag         = True
    draw_antitag     = True

    try:
        npz = np.load(filename)
    except:
        print "could not load ", filename, " as .npz file."
        return
    timestamp      = npz['timestamp']
    region         = npz['region']   
    py             = npz['py']       
    px             = npz['px']       
    delta          = npz['delta']    
    total_exposure = int(npz['total_exposure'])

    trig = np.array([region[i,center_index] for i in range(region.shape[0])])
    sum  = np.array([np.sum(region[i,:]) for i in range(region.shape[0])])

    h,bins = np.histogram(delta[sum>=50], bins=121, range=(-60,60))
    delta_dn = bins[np.argmax(h)]
    delta_up = bins[np.argmax(h)+1]
    
    if (plot_delta):
        err = h**0.5
        cbins = 0.5*(bins[:-1] + bins[1:])
        plt.errorbar(cbins,h,yerr=err,color="black",fmt="o",label="sum > 50")
        plt.ylabel("phone images")
        plt.xlabel("delta t [s]")
        plt.title("Time difference between smartphone and muon hodoscope")
        s = "exposure:  " + str(total_exposure) + " s"
        mark_plot(0.7,0.95,s)
        mark_plot(0.01,0.95,"region sum >= 50 electrons")
        #plt.legend(numpoints=1)
        #plt.xlim(-2.0,2.0)
        plt.savefig("plots/delta.pdf")
        plt.show()

    if (plot_delta_fail):
        h,bins = np.histogram(delta[sum<50], bins=121, range=(-60,60))
        err = h**0.5
        cbins = 0.5*(bins[:-1] + bins[1:])
        plt.errorbar(cbins,h,yerr=err,color="red",fmt="o",label="sum > 50")
        plt.ylabel("phone images")
        plt.xlabel("delta t [s]")
        plt.title("Time difference between smartphone and muon hodoscope")
        s = "exposure:  " + str(total_exposure) + " s"
        mark_plot(0.7,0.95,s)
        mark_plot(0.01,0.95,"region sum < 50 electrons")
        #plt.legend(numpoints=1)
        plt.savefig("plots/delta_fails.pdf")
        plt.show()

    muon_tag = (delta >= delta_dn) & (delta <= delta_up) & (sum >= 50)
    muon_antitag = ((delta < delta_dn) | (delta > delta_up)) & (sum >= 50) 

    if (plot_sum):
        h,bins = np.histogram(np.clip(sum[muon_tag],0,500), bins=10, range=(0,500))
        err = h**0.5
        cbins = 0.5*(bins[:-1] + bins[1:])
        plt.errorbar(cbins,h,yerr=err,color="red",fmt="o",label="sum > 50")
        plt.ylabel("tagged muons")
        plt.xlabel("deposited electrons")
        plt.title("Electrons deposited in depletion region by muon.")
        plt.savefig("plots/sum.pdf")
        plt.show()

    if (plot_pos):
        plt.plot(px[muon_tag],py[muon_tag],"bo")
        plt.xlim(0,width)
        plt.ylim(0,height)
        plt.savefig("plots/pos.pdf")
        plt.show()
    
    if (draw_tag):
        cand      = region[muon_tag,:]
        cand      = cand.reshape((-1,(2*dx+1),(2*dy+1)))
        num = np.sum(muon_tag)
        print "number of anti-tagged candidates is ", num
        if (num > 100):
            num = 100
        _draw_regions(cand,num,True)

    if (draw_antitag):
        cand      = region[muon_antitag,:]
        cand      = cand.reshape((-1,(2*dx+1),(2*dy+1)))
        num = np.sum(muon_antitag)
        print "number of anti-tagged candidates is ", num
        if (num > 100):
            num = 100
        _draw_regions(cand,num,False)
            

    
if __name__ == "__main__":
    example_text = '''examples:

    ./show_mean_var.py ./data/combined/small_dark.npz --max_var=30 --max_mean=5'''
    
    parser = argparse.ArgumentParser(description='Plot mean and variance.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', metavar='FILE', nargs='+', help='file to process')
    parser.add_argument('--skip_default',action="store_true", help="skip the default plot or plots.")
    parser.add_argument('--sandbox',action="store_true", help="run sandbox code and exit (for development).")
    parser.add_argument('--max_var',  type=float, default=800,help="input files have not been preprocessed.")
    parser.add_argument('--max_mean', type=float, default=200,help="input files have not been preprocessed.")
    args = parser.parse_args()

    
    init(args)

    for filename in args.files:
        print "processing file:  ", filename
        process(filename, args)




