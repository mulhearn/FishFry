import numpy as np

# find local maximum satisfying:
# > > >
# > X =
# = = =
# where = denotes >=.
# For any shape dx/dy

def local_maximum(region,dx,dy):
     #central bin:
     icenter = dx + dy + 2*dx*dy
     gte = np.array([],dtype=int)
     gt = np.array([],dtype=int)
     w = (2*dx + 1)
     h = (2*dy + 1)
     for index in np.delete(range(w*h),icenter):
          ix = index % w
          iy = index / w          
          if (iy < ix):
               gte = np.append(gte, index)
          elif (iy > ix):
               gt = np.append(gt, index)
          elif (index < icenter):
               gte = np.append(gte, index)
          else:
               gt = np.append(gt, index)
     region_size = region.shape[0]
     local_max = np.array([((region[i,icenter] > np.max(region[i,gt])) & (region[i,icenter] >= np.max(region[i,gte]))) for i in range(region_size)])
     return local_max
