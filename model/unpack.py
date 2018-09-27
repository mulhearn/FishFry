import numpy as np

header_map = {
    "version"       : 0,
    "images"        : 1,
    "width"         : 2,
    "height"        : 3,
    "cell_size"     : 4,

}

def unpack_all(filename):
    with open(filename) as f:
        hsize       = np.fromfile(f,dtype="i4",count=1)[0]
        version     = np.fromfile(f,dtype="i4",count=1)[0]
        print hsize
        print version
        header      = np.fromfile(f,dtype="i4",count=hsize)
        header      = np.insert(header, 0, version)

        images    = interpret_header(header, "images")
        cell_size = interpret_header(header, "cell_size")

        depletion   = np.fromfile(f,dtype="f4",count=1)[0]
        print depletion

        slab   = np.fromfile(f,dtype="f4",count=1)[0]
        print slab

        edep = np.fromfile(f,dtype="f4",count=cell_size*cell_size*images)
        edep = edep * 1E6 # convert to eV
        edep = edep / 3.6 # convert to number of electrons
        edep = edep.reshape((-1,cell_size,cell_size))
        return header,depletion,slab,edep

def unpack_header(filename):
    header,depletion,slab,edep = unpack_all(filename)
    return header

def interpret_header(header, param):    
    if param in header_map:
        return header[header_map[param]]
    else:
        print "ERROR:  invalid parameter ", param
        exit(0)

def show_header(header):    
    pass
    hsize       = header.size
    print "additional header size:         ", hsize-1
    print "version:                        ", interpret_header(header, "version")
    print "images:                         ", interpret_header(header, "images")
    print "width:                          ", interpret_header(header, "width")
    print "height:                         ", interpret_header(header, "height")
    print "cell_size:                      ", interpret_header(header, "cell_size")
