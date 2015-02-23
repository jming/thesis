from __future__ import division

import numpy as np
import sys
import os
import errno
from numpy.random import RandomState
import random_projection as rp
# import gram_schmidt_stable as gs 
# import gram_schmidt_convhull as gs
import gram_schmidt_convhull_v2 as gs
import time

def findAnchors(Q, K, params, candidates):
    # Random number generator for generating dimension reduction
    prng_W = RandomState(params.seed)
    checkpoint_prefix = params.checkpoint_prefix
    new_dim = params.new_dim

    # np.savetxt("result_out.20.Q_orig", Q)
    print 'calculating variances', time.time()
    # var = gs.Calc_Vars(Q, 10)
    # np.savetxt('result_out.20.var', var)
    var = np.loadtxt('result_out.20.var')

    # row normalize Q
    row_sums = Q.sum(1)
    for i in xrange(len(Q[:, 0])):
        Q[i, :] = Q[i, :]/float(row_sums[i])    

    # Reduced dimension random projection method for recovering anchor words
    # Q_red = rp.Random_Projection(Q.T, new_dim, prng_W)
    # Q_red = Q_red.T

    np.savetxt("result_out.20.Q_bar", Q)

    (anchors, anchor_indices) = gs.Projection_Find(Q, K, candidates, var)
    # (anchors, anchor_indices) = gs.Projection_Find(Q_red, K, candidates)
    # anchor_indices = [7.,24.,2058.,1595.,787.,2319.,1486.,2084.,20.,669.,2209.,561.,427.,2056.,936.,2770.,2691.,29.,2671.,2134.]
    anchor_indices = [int(a) for a in anchor_indices]

    # restore the original Q
    for i in xrange(len(Q[:, 0])):
        Q[i, :] = Q[i, :]*float(row_sums[i])

    return anchor_indices


