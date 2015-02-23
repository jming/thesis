from __future__ import division
import numpy as np
import lsqlin
import time
import scipy.optimize

def Projection_Find(M_orig, r, candidates, var):

    print 'initializing variables', time.time()

    # set num reps/configs
    reps = 1
    configs = 1

    dim_n = M_orig[:, 0].size
    dim = M_orig[0, :].size

    # print n,dim

    M = M_orig.copy()
    
    # stored recovered anchor words
    anchor_sets = np.zeros((reps*configs*r, r))
    # print anchor_sets.shape

    # store the basis vectors of the subspace spanned by the anchor word vectors
    basis = np.zeros((r-1, dim))

    print 'inializing coordinate system', time.time()

    # find the farthest point p1 from the origin
    max_dist = 0
    #for i in range(0, n):
    for i in candidates:
        dist = np.dot(M[i], M[i])
        if dist > max_dist:
            max_dist = dist
            anchor_sets[0][0] = i

    # let p1 be the origin of our coordinate system
    #for i in range(0, n):
    for i in candidates:
        M[i] = M[i] - M_orig[0]

    print 'finding elements of basis', time.time()

    # find the elements of the basis greedily
    # find the farthest point from p1
    max_dist = 0
    #for i in range(0, n):
    for i in candidates:
        dist = np.dot(M[i], M[i])
        if dist > max_dist:
            max_dist = dist
            anchor_sets[0][1] = i
            basis[0] = M[i]/np.sqrt(np.dot(M[i], M[i]))

    # find reminaing by distance from basis
    # stabilized gram-schmidt which finds new anchor words to expand our subspace
    for j in range(1, r - 1):

        # project all the points onto our basis and find the farthest point
        max_dist = 0
        #for i in range(0, n):
        for i in candidates:
            M[i] = M[i] - np.dot(M[i], basis[j-1])*basis[j-1]
            dist = np.dot(M[i], M[i])
            if dist > max_dist:
                max_dist = dist
                anchor_sets[0][j+1] = i
                basis[j] = M[i]/np.sqrt(np.dot(M[i], M[i]))

    # updating anchors
    print 'updating anchors', time.time()

    # number of repititions
    for rep in range(0,reps):

        print 'rep', rep, time.time()

        # number of anchors
        for j in range(0, r-1):

            print 'anchor', j, time.time()

            # previous set number
            set_n = rep*(r-1)+j
            print 'setn', set_n

            # create config table for storing
            config_table = np.zeros((configs, dim_n, dim))
            config_avgs = np.zeros((configs, len(candidates)))

            for n in range(0, configs):

                print 'config', n, time.time()

                # create new configuration
                config = create_config(M, var)
                config_table[n] = config

                np.savetxt('log.config'+str(n), config)

                # try replacing anchor j in configuration n
                for i,candidate in enumerate(candidates):

                    print 'candidate', i, time.time()

                    # try using candidate basis
                    active_set = np.concatenate((anchor_sets[set_n][:j], [candidate], anchor_sets[set_n][j+1:]))

                    # count number of points included in this configuration
                    # TODO: should this be counting how many from the old config are in the new config???
                    count = count_incl(config, active_set)

                    # store the calculated values
                    print count
                    config_avgs[n][i] = count

                    np.savetxt('log.anchor_sets', anchor_sets)

            # find the averages of all configurations across candidates
            max_incl = candidates[np.argmax(config_avgs.sum(axis=0))]
            # max_incl = candidates[max(config_avgs[n])]

            # replace with the anchor with the highest average
            # print anchor_sets.shape
            # print set_n, j, max_incl, set_n
            anchor_sets[set_n+1] = np.concatenate((anchor_sets[set_n][:j], [max_incl], anchor_sets[set_n][j+1:]))
            print anchor_sets[set_n+1]
            np.savetxt("log.anchor_sets", anchor_sets)
                
    # TODO: test the candidate configurations before selecting anchor_indices

    print 'finishing up'

    np.savetxt("log.anchor_sets", anchor_sets)

    # convert numpy array to python list
    anchor_indices = anchor_sets[-1]
    print anchor_indices
    anchor_words = [M_orig[x] for x in anchor_indices]
    anchor_indices_list = [ai for ai in anchor_indices]

    # for i in range(r):
        # anchor_indices_list.append(anchor_indices[i])
    
    return (anchor_words, anchor_indices_list)

def create_config(M, var):

    return 2 * var * np.random.random_sample((M.shape)) - var

def in_conv_hull(b, p):

    # print b.shape, p.shape

    def mfunc(x):
        return np.dot(x,b) - p

    # def nfunc(x):
    #     return np.dot((np.dot(x,b) - p),(np.dot(x,b) - p).T)[0,0]

    def func(x, sign=1.0):
        # print np.linalg.norm(mfunc(x)), np.dot((np.dot(x,b) - p),(np.dot(x,b) - p).T)
        return np.linalg.norm(mfunc(x), ord='fro')
        # return nfunc(x)

    bds = np.array([(0,1) for i in range(b[:,0].size)])

    cons = ({'type' : 'eq',
            'fun' : lambda x: np.array([sum(x) - 1]),
            'jac' : lambda x: np.array([1] * x.size)})
            # {'type' : 'ineq',
            # 'fun' : lambda x: np.array([-1 * sum(x <= 0)]),
            # 'jac' : lambda x: np.array([1] * x.size)})

    n = b[:,0].size
    x0 = np.array([1./n]*n)

    res = scipy.optimize.minimize(func, x0, constraints=cons, bounds=bds)

    # print 
    # print res
    # print b, p
    # print np.linalg.norm(mfunc(res.x), ord='fro')**2
    return np.linalg.norm(mfunc(res.x), ord='fro')**2 <= 1e-7
    # print np.linalg.norm(np.dot(res.x , b) - p) ** 2

    # return np.linalg.norm(mfunc(res.x)) ** 2 <= 1e-7
    # return nfunc(res.x) <= 1e-7
    # return True

    # print basis
    # print point

    # m = basis[:,0].size
    # n = basis[0,:].size
    
    # C = np.array(basis)
    # d = np.array(point)
    # A = None
    # b = None

    # Aeq = np.ones((1, n))
    # beq = np.ones(1)
    # lb = np.zeros((n, 1))
    # ub = np.zeros((n, 1))

    # x = lsqlin.lsqlin(C, d, A=A, b=b, Aeq=Aeq, beq=beq, lb=lb, ub=ub)

    # return np.linalg.norm(x)**2 <= 1e7

def count_incl(config, anchor_set):

    incl = []
    anchors = np.matrix([config[a] for a in anchor_set])

    for point in config:
        incl.append(in_conv_hull(anchors, point))

    # print incl 
    return sum(incl)


# TODO: should calculate variances beforehand
def Calc_Vars(M, n):

    rows,cols = M.shape
    var = np.zeros((rows, cols))
    
    for i in range(rows):
        
        p_i = sum(M[i])
        
        for j in range(cols):
            
            if i == j:
                
                var[i][j] = n * ( -2 * p_i**2 + 8 * p_i**3 - 6 * p_i**4) +\
                            n**3 * (4 * p_i**3 - 4 * p_i**4) +\
                            n**2 * (2 * p_i**2 - 12 * p_i**3 + 10 * p_i**4)
            else:
                
                p_j = sum(M[j])
                var[i][j] = n**3 * (p_i**2 * p_j + p_i * p_j**2 - 4 * p_i**2 * p_j**2) +\
                            n**2 * (p_i * p_j + 10 * p_i**2 * p_j**2 - 3 * ( p_i**2 * p_j + p_i * p_j**2)) +\
                            n * (-p_i * p_j - 6 * p_i**2 * p_j**2 + 2 * (p_i**2 * p_j + p_i * p_j**2))
    
    return var


#  some practice methods

if __name__ == '__main__':

    '''
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

    print Projection_Find(M_orig, rs, candidates, variances)
    '''

    pass

    # # basis = np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]])
    # # # point = np.array([0.9, 0.05, 0.05])
    # # point = np.array([0.3, 0.3, 0.4])
    # # print in_conv_hull(basis, point)
    # # print res
    # # print np.linalg.norm(np.dot(res.x,basis)-point)**2
    # # print res.x
    # # print np.dot(res.x,basis)
    # # print np.linalg.norm(np.dot(res.x,basis)-point)**2 <= 1e-7

    # # print 'loading stored values', time.time()

    # # M = np.loadtxt('../result_out.20.M')
    # # candidates = np.loadtxt('../result_out.20.candidates')
    # # var = np.loadtxt('../result_out.20.var')

    # # print Projection_Find(M, 20, candidates, var)


