import numpy as np

header_map = {
    "images"      : 0,
    "num_files"   : 1,
    "ifile"       : 2,
    "width"       : 3,
    "height"      : 4,
    "sens"        : 5,
    "exposure"    : 6,
    "step_pixels" : 7,
    "offset"      : 8,
    "num_pixels"  : 9,
    "pixel_start" : 10,
    "pixel_end"   : 11
}

def unpack_all(filename):
    with open(filename) as f:
        hsize       = np.fromfile(f,dtype=">i4",count=1)[0]
        version     = np.fromfile(f,dtype=">i4",count=1)[0]
        header      = np.fromfile(f,dtype=">i4",count=hsize)
        num         = (header[header_map["pixel_end"]] - header[header_map["pixel_start"]])
        #print "reading data from ", num, " pixels."
        sum         = np.fromfile(f,dtype=">i8",count=num)
        ssq         = np.fromfile(f,dtype=">i8",count=num)
        #print "num sum:  ", len(sum)
        #print "num ssq:  ", len(ssq)
        if ((num != len(ssq)) or (num != len(sum))):
            print "data format error... exiting."
            exit(0)

        return version,header,sum,ssq

def unpack_header(filename):
    version,header,sum,ssq = unpack_all(filename)
    return header

def interpret_header(header, param):    
    if param in header_map:
        return header[header_map[param]]
    else:
        print "ERROR:  invalid parameter ", param
        exit(0)

def get_pixel_indices(header):
    offset      = interpret_header(header, "offset")
    step_pixels = interpret_header(header, "step_pixels")
    pixel_start = interpret_header(header, "pixel_start")
    pixel_end   = interpret_header(header, "pixel_end")
    index = np.zeros(pixel_end-pixel_start,dtype=int)
    for i in range(pixel_start, pixel_end):
        index[i-pixel_start] = offset + i*step_pixels
    return index

def show_header(header):    
    hsize       = header.size
    print "additional header size:         ", hsize
    print "images:                         ", interpret_header(header, "images")
    print "width:                          ", interpret_header(header, "width")
    print "height:                         ", interpret_header(header, "height")
    print "sensitivity:                    ", interpret_header(header, "sens")
    print "exposure:                       ", interpret_header(header, "exposure")
    print "num files:                      ", interpret_header(header, "num_files")
    print "file index:                     ", interpret_header(header, "ifile")
    print "offset:                         ", interpret_header(header, "offset")
    print "step_pixels:                    ", interpret_header(header, "step_pixels")
    print "num_pixels:                     ", interpret_header(header, "num_pixels")
    print "pixel_start:                    ", interpret_header(header, "pixel_start")
    print "pixel_end:                      ", interpret_header(header, "pixel_end")

