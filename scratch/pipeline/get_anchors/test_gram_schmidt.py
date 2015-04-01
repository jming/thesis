import numpy as np
import gram_schmidt_convhull as gsc
import gram_schmidt_stable as gss

if __name__ == '__main__':

    print 'building test data'

    M_orig = []
    for i in range(10):
        row = np.random.rand(100)
        row = [r/sum(row) for r in row]
        M_orig.append(row)
    M_orig = np.array(M_orig)

    rs = 5
    
    candidates = [x for x in range(7)]

    variances = []
    for i in range(10):
        row = np.random.rand(100)
        row = [r/10000 for r in row]
        variances.append(row)
    variances = np.array(variances)

    print 'testing'

    aw_gsc, ai_gsc = gsc.Projection_Find(M_orig, rs, candidates, variances)
    aw_gss, ai_gss = gss.Projection_Find(M_orig, rs, candidates)

    print ai_gsc, ai_gss