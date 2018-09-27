#! /usr/bin/env python

# dump the header from run data

import sys
from unpack import *

import argparse


def process(filename,args):
    header = unpack_header(filename)
    show_header(header)

if __name__ == "__main__":

    example_text = '''examples:

    ./dump_header.py pdout.dat
'''    
    parser = argparse.ArgumentParser(description='Combine multiple pixelstats data files.', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('files', metavar='FILE', nargs='+', help='file to process')
    parser.add_argument('--sandbox',action="store_true", help="run trial code")
    args = parser.parse_args()

    for filename in args.files:
        print "processing file:  ", filename
        process(filename, args)

        
