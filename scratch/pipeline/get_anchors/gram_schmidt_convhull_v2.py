import numpy as np
import scipy.optimize
import random
import gram_schmidt_stable as gss
import time

def Projection_Find(M_orig, r, candidates, var):
    
    M = M_orig.copy()
    
    dim_n, dim_m = M_orig.shape
    
    configs = 10
    # tries = 20
    tries = 10
    k_star = 5
    
    config_tables = np.zeros((tries/k_star, configs, dim_n, dim_m))
    # config_tries = np.zeros((tries/k_star, 2, configs, dim_n, dim_m))
    anchor_sets = np.zeros((tries+1, r))
    evals = np.zeros((tries+1, configs, dim_n))
    evals_configs = np.zeros((tries/k_star, configs, dim_n))
    set_evals = np.zeros(tries+1)
    
    # find basic anchorset
    print 'initializing basis', time.time()
    
    words, basis = gss.Projection_Find(M, r, candidates)
    anchor_sets[0] = basis
    print M_orig.shape, anchor_sets[0].shape
    # set_incl = evaluate_set(M_orig, anchor_sets[0])
    # set_evals[0] = sum(set_incl)
    # print 'try orig', 0, set_evals[0], anchor_sets[0]

    # write to text file
    np.savetxt('log.set_evals', set_evals)
    np.savetxt('log.anchor_sets', anchor_sets)
    
    # iterate on this anchor set
    print 'iterate on anchor set', time.time()
    for k in range(tries):
        
        # create a new set of configurations
        if k % k_star == 0:
            for n in range(configs):
                config = create_config(M, var)
                config_tables[k/k_star][n] = config
                evals_configs[k/k_star][n] = evaluate_set(config, anchor_sets[0])
                # print len(evaled), evaled.shape
                # evals_configs[k/k_star][n] = evaled
            np.savetxt('log.evals_configs', evals_configs.flatten())
        
        if k == 0:
            active_set = anchor_sets[0]
            # evals = np.zeros(configs)
            for i,config in enumerate(config_tables[k/k_star]):
                evals[k][i] = evaluate_set(config, active_set)
            # print 'evals', evals
            set_evals[k] = np.sum(evals[k,:])/len(evals[k,:])

            print 'try', 0, set_evals[0], anchor_sets[0]
            # set_evals[k] = 1.

        # select an anchor to swap out
        while True:

            so = select_anchor(anchor_sets[k], var)
            so_val = anchor_sets[k][so]
            # select an anchor to swap in
            # candidates_less = [c for c in candidates if c not in anchor_sets[k]]
            candidates_less = list(set(candidates) - set(anchor_sets[k]))
            si = select_anchor(candidates_less, var, anchor_sets[k][so], M)
            si_val = candidates_less[si]

            active_set = np.concatenate((anchor_sets[k][:so], [si_val], anchor_sets[k][so+1:]))
            # print active_set
            # print active_set in anchor_sets
            # print anchor_sets
            # if active_set not in anchor_sets:
            if not any((active_set == x).all() for x in anchor_sets):
                # print 'out'
                break
        
        # print 'so,si', so, so_val, si, si_val
        
        # evaluate the goodness of this swap
        # evals = np.zeros(configs)
        for i,config in enumerate(config_tables[k/k_star]):
            evals[k+1][i] = evaluate_set(config, active_set)
        # print 'evals', evals
        set_evals[k+1] = np.sum(evals[k+1,:])/len(evals[k+1,:])
        # set_evals[k+1] = sum(evals)/len(evals)

        print 'try', k+1, time.time(), set_evals[k+1], active_set

        # decide on whether to switch up swap
        if set_evals[k+1] <= set_evals[k]:
            anchor_sets[k+1] = active_set
        else:
            anchor_sets[k+1] = anchor_sets[k]  
            set_evals[k+1] = set_evals[k]
        
        # print 'try orig', k+1, time.time(), evaluate_set(M_orig, active_set), active_set
        np.savetxt('log.evals', evals.flatten())
        np.savetxt('log.set_evals', set_evals)
        np.savetxt('log.anchor_sets', anchor_sets)      
        
    print 'finishing up', time.time()
    
    anchor_indices = anchor_sets[-1]
    anchor_words = [M_orig[x] for x in anchor_indices]
    anchor_indices_list = [int(ai) for ai in anchor_indices]
    
    return (anchor_words, anchor_indices_list)

def create_config(M, var):
    # TODO: try sqrt
    # return 2 * var * np.random.random_sample((M.shape)) - var
    # var_sqrt = np.sqrt(var)
    # print 'var', var[0]
    # print 'varsqrt', var_sqrt[0]
    # var_sqrt = np.log(var)
    # new_config = np.exp(2 * var_sqrt * np.random.random_sample((M.shape)) - var_sqrt)
    # number of less than 0
    # print 'new config'
    new_config = np.zeros(M.shape)
    col_sums = M.sum(0)
    # V = M.shape[0]
    # print 'V', V
    # sizes = np.array([1./V for v in range(V)])
    # print 'sizes', sizes
    for i,row in enumerate(M):
        # alphas = row + sizes
        alphas = row + col_sums
        # print row, col_sums, alphas
        new_config[i] = np.random.dirichlet(alphas)
    # print 'new config created'


    # zeros = np.where(M <= 0)
    
    # print zeros
    # for r,c in zip(zeros[0], zeros[1]):
    #     M[r,c] = np.float64(0.0000001)
        # print M[r,c]


    # print 'zeros', len(np.where(M == 0))
    # print 'less than 0', len(np.where(M < 0)[0]), 'equal 0', len(np.where(M == 0)[0])
    # new_config = np.exp(2 * var * np.random.random_sample((M.shape)) - var + np.log(M))

    # new_config = 2 * var * np.random.random_sample((M.shape)) - var + M
    # print 'less than 0', len(np.where(new_config < 0)[0]), 'equal 0', len(np.where(new_config == 0)[0])
    # min_val = np.min(new_config)
    # new_config = abs(min_val) + new_config

    # print 'min', min_val, 'new', np.min(new_config), np.max(new_config), 'old', np.min(M), np.max(M)
    # # print 'less than 0', len(np.where(new_config < 0)[0])
    # # new_config = np.where(new_config >= 0, new_config, 0)

    #normalize
    Q = new_config
    row_sums = Q.sum(1)
    for i in xrange(len(Q[:, 0])):
        Q[i, :] = Q[i, :]/float(row_sums[i])

    return Q

def select_anchor(options, var, basis_v=None, M=None):

    # probs is 1/sum(variance) + distance
    if basis_v and M != None:
        dists = []
        for i in options:
            Mi = M[i] - np.dot(M[i], basis_v)*basis_v
            dist = np.dot(Mi, Mi)
            dists.append(dist)
        # print 'dists', dists
        if sum(dists) != 0:
            dists = [d/sum(dists) for d in dists]
        varss = [1/sum(var[i]) for i in options]
        varss = [v/sum(varss) for v in varss]
        probs = [(a+b)/2 for a,b in zip(dists, varss)]
            # M[i] = 
            # dist = np.dot(M[i], M[i])

            # TODO: scale this
            # print 1/(sum(var[i])), dist
            # probs.append(1/(sum(var[i])) + dist)

    # probs is 1/sum(variance)
    # because sqrt(prod(var)) is too small it becomes 0
    else:
        probs = [1/sum(var[i]) for i in options]
    
    # print 'var', [sum(var[i]) for i in options]
    # print 'probs before', probs
    probs = [p / sum(probs) for p in probs]
    # print 'probs after', probs

    return weighted_random(probs)

def weighted_random(probs):
    
    r = random.random()
    index = 0
    while r >= 0 and index < len(probs):
        r -= probs[index]
        index += 1
    
    return index - 1

def evaluate_set(config, anchor_set):

    # TODO: try to test less points 
    
    incl = []
    anchors = np.matrix([config[a] for a in anchor_set])
    
    for point in config:
        incl.append(in_conv_hull(anchors, point))
    
    # np.savetxt('')

    # return sum(incl)
    return incl

def in_conv_hull(b, p):

    # print 'anchors', b
    # print 'point', p

    def mfunc(x):
        return np.dot(x,b) - p

    def func(x, sign=1.0):
        return np.linalg.norm(mfunc(x), ord='fro')

    bds = np.array([(0,1) for i in range(b[:,0].size)])

    cons = ({'type' : 'eq',
            'fun' : lambda x: np.array([sum(x) - 1]),
            'jac' : lambda x: np.array([1] * x.size)})

    n = b[:,0].size
    x0 = np.array([1./n]*n)

    # print np.linalg.norm(mfunc(res.x), ord='fro')**2 <= 1e-7

    res = scipy.optimize.minimize(func, x0, constraints=cons, bounds=bds)
    # print np.linalg.norm(mfunc(res.x), ord='fro')**2

    # return np.linalg.norm(mfunc(res.x), ord='fro')**2 <= 1e-7
    # return np.linalg.norm(mfunc(res.x), ord='fro')**2
    return (np.linalg.norm(mfunc(res.x), ord=1)**2)
    # /np.linalg.norm(p, ord=1)

if __name__ == '__main__':

    # active_set = [  284.  ,  91. , 2058. , 1595. , 1409. , 2319. , 1486. , 2084.  ,  20. ,  669.,  2236.,  1873. , 1638. , 2056.  , 936.,  2770.,  2856.,    29.,  2671.,  2134.]

    # print 'loading'
    # M = np.loadtxt("../result_out.20.Q_bar")
    # var = np.loadtxt("../result_out.20.var")

    # print 'calc'
    # config = create_config(M,var)

    # print evaluate_set(config, active_set)



    print 'building test data'

    M_orig = []
    for i in range(20):
        row = np.random.rand(100)
        row = [r/sum(row) for r in row]
        M_orig.append(row)
    M_orig = np.array(M_orig)

    rs = 5

    candidates = [x for x in range(15)]

    variances = []
    for i in range(20):
        row = np.random.rand(100)
        row = [r/1000 for r in row]
        variances.append(row)
    variances = np.array(variances)

    a, b = Projection_Find(M_orig, rs, candidates, variances)
    print b


