import numpy as np

header_map = {
    "images"          : 0,
    "num_files"       : 1,
    "ifile"           : 2,
    "width"           : 3,
    "height"          : 4,
    "sens"            : 5,
    "exposure"        : 6,
    "num_partition"   : 7,
    "partition_index" : 8,
    "pixel_start"     : 9,
    "pixel_end"       : 10,
    "sample_step"     : 11,
}

def unpack_all(filename):
    with open(filename) as f:
        hsize       = np.fromfile(f,dtype=">i4",count=1)[0]
        print "header size:  ", hsize
        version     = np.fromfile(f,dtype=">i4",count=1)[0]
        header      = np.fromfile(f,dtype=">i4",count=hsize)
        num         = (header[header_map["pixel_end"]] - header[header_map["pixel_start"]])
        ds          = header[header_map["sample_step"]]
        if (ds > 1):
            num = 1 + (num - 1) / ds
        print "reading data from ", num, " pixels."
        sum         = np.fromfile(f,dtype=">i4",count=num)
        ssq         = np.fromfile(f,dtype=">i8",count=num)
        print "num sum:  ", len(sum)
        print "num ssq:  ", len(ssq)
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
    pixel_start = interpret_header(header, "pixel_start")
    pixel_end   = interpret_header(header, "pixel_end")
    sample_step = interpret_header(header, "sample_step")
    num = pixel_end - pixel_start;
    if (sample_step > 1):
            num = 1 + (num - 1) / sample_step
    index = np.zeros(num,dtype="int")
    for i in range(num):
        index[i] = pixel_start + i*sample_step
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
    print "num_partition:                  ", interpret_header(header, "num_partition")
    print "parition_index:                 ", interpret_header(header, "partition_index")
    print "pixel_start:                    ", interpret_header(header, "pixel_start")
    print "pixel_end:                      ", interpret_header(header, "pixel_end")
    print "sample_step:                    ", interpret_header(header, "sample_step")

