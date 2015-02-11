from __future__ import division
import numpy as np
import lsqlin
import time
import scipy.optimize

def Projection_Find(M_orig, r, candidates, var):

    print 'initializing variables', time.time()

    # set num reps/configs
    reps = 1
    configs = 10

    n = M_orig[:, 0].size
    dim = M_orig[0, :].size

    M = M_orig.copy()
    
    # stored recovered anchor words
    anchor_sets = np.zeros((reps*configs+1, r))

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

    for rep in range(0,reps):
        for j in range(0, r-1):

            # set number
            set_n = rep*(r-1)+j

            # create config table for storing
            config_table = np.zeros((configs, r-1, dim))
            config_avgs = np.zeros((len(candidates), configs))

            for n in range(0, configs):

                print 'config', n, time.time()

                # create new configuration
                config = create_config(M, var)

                for i in candidates:

                    print 'candidate', i, time.time()

                    # try using candidate basis
                    active_set = np.concatenate((anchor_sets[set_n][:j], [i], anchor_sets[set_n][j+1:]))

                    # count number of points included in this configuration
                    # TODO: should this be counting how many from the old config are in the new config???
                    count = count_incl(config, active_set)

                # find the averages of all configurations across candidates
                max_incl = np.argmax(config_avgs.sum(axis=1))

                # replace with the anchor with the highest average
                anchor_sets[set_n+1] = np.concatenate((anchor_sets[set_n][:j], [max_incl], anchor_sets[set_n][j+1:]))
                print anchor_sets[set_n+1]
                
    print 'finishing up'

    # convert numpy array to python list
    anchor_indices = anchor_sets[-1]
    anchor_words = [M_orig[x] for x in anchor_indices]

    anchor_indices_list = []
    for i in range(r):
        anchor_indices_list.append(anchor_indices[i])
    
    return (anchor_words, anchor_indices_list)

def create_config(M, var):

    return 2 * var * np.random.random_sample((M.shape)) - var

def in_conv_hull(b, p):

    def mfunc(x):
        return np.dot(x,b) - p

    def func(x, sign=1.0):
        return np.linalg.norm(mfunc(x))

    cons = ({'type' : 'eq',
            'fun' : lambda x: np.array([sum(x) - 1]),
            'jac' : lambda x: np.array([1] * x.size)},
            {'type' : 'ineq',
            'fun' : lambda x: np.array([-1 * sum(x < 0)]),
            'jac' : lambda x: np.array([1] * x.size)})

    n = b[:,0].size
    x0 = np.array([1./n]*n)

    res = scipy.optimize.minimize(func, x0, constraints=cons)

    return np.linalg.norm(np.dot(res.x , b) - p) ** 2 <= 1e-6

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

    return sum(incl)


# TODO: should calculate variances beforehand
def calc_vars(M, n):
    
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

    print 'loading stored values', time.time()

    M = np.loadtxt('../result_out.20.M')
    candidates = np.loadtxt('../result_out.20.candidates')
    var = np.loadtxt('../result_out.20.var')

    print Projection_Find(M, 20, candidates, var)



