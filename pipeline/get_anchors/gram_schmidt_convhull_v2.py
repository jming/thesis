import numpy as np
import scipy.optimize
import random
import gram_schmidt_stable as gss

def Projection_Find(M_orig, r, candidates, var):
    
    M = M_orig.copy()
    
    dim_n, dim_m = M_orig.shape
    
    configs = 10
    tries = 20
    k_star = 5
    
    config_tables = np.zeros((k_star, configs, dim_n, dim_m))
    anchor_sets = np.zeros((tries+1, r))
    set_evals = np.zeros(tries+1)
    
    # find basic anchorset
    print 'initializing basis'
    
    words, basis = gss.Projection_Find(M, r, candidates)
    anchor_sets[0] = basis
    set_evals[0] = evaluate_set(M_orig, anchor_sets[0])
    
    print 'try', 0, set_evals[0], anchor_sets[0]

    # TODO: write to text file
    np.savetxt('log.set_evals')
    
    # iterate on this anchor set
    print 'iterate on anchor set'
    for k in range(tries):
        
        # create a new set of configurations
        if k % k_star == 0:
            for n in range(configs):
                config = create_config(M, var)
                config_tables[k/k_star][n] = config
        
        # select an anchor to swap out
        so = select_anchor(anchor_sets[k], var)
        # select an anchor to swap in
        si = select_anchor([c for c in candidates if c != so], var)
        
        print 'so,si', so, si
        
        # evaluate the goodness of this swap
        active_set = np.concatenate((anchor_sets[k][:so], [si], anchor_sets[k][so+1:]))
        evals = np.zeros(configs)
        for i,config in enumerate(config_tables[k/k_star]):
            evals[i] = evaluate_set(config, active_set)
        set_evals[k+1] = sum(evals)/len(evals)
        
        print 'try', k+1, set_evals[k+1]
        print active_set

        # TODO: write to text file
        
        # decide on whether to switch up swap
        if set_evals[k+1] > set_evals[k]:
            anchor_sets[k+1] = active_set
        else:
            anchor_sets[k+1] = anchor_sets[k]        
        
    print 'finishing up'
    
    anchor_indices = anchor_sets[-1]
    anchor_words = [M_orig[x] for x in anchor_indices]
    anchor_indices_list = [ai for ai in anchor_indices]
    
    return (anchor_words, anchor_indices_list)

def create_config(M, var):
    return 2 * var * np.random.random_sample((M.shape)) - var

def select_anchor(options, var):
    
    probs = [sum(var[i]) for i in options]
    return weighted_random(probs)

def weighted_random(probs):
    
    r = random.random()
    index = 0
    while r >= 0 and index < len(probs):
        r -= probs[index]
        index += 1
    
    return index - 1

def evaluate_set(config, anchor_set):
    
    incl = []
    anchors = np.matrix([config[a] for a in anchor_set])
    
    for point in config:
        incl.append(in_conv_hull(anchors, point))
        
    return sum(incl)

def in_conv_hull(b, p):

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

    res = scipy.optimize.minimize(func, x0, constraints=cons, bounds=bds)

    return np.linalg.norm(mfunc(res.x), ord='fro')**2 <= 1e-7

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
	    row = [r/1000 for r in row]
	    variances.append(row)
	variances = np.array(variances)

	a, b = Projection_Find(M_orig, rs, candidates, variances)
	print b


