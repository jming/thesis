import scipy.io
from fastRecover import do_recovery
import gram_schmidt_convhull_v2 as gs
import time
import sys
import numpy as np


class Params:

    def __init__(self, filename):
        self.log_prefix=None
        self.checkpoint_prefix=None
        self.seed = int(time.time())

        for l in file(filename):
            if l == "\n" or l[0] == "#":
                continue
            l = l.strip()
            l = l.split('=')
            if l[0] == "log_prefix":
                self.log_prefix = l[1]
            elif l[0] == "max_threads":
                self.max_threads = int(l[1])
            elif l[0] == "eps":
                self.eps = float(l[1])
            elif l[0] == "checkpoint_prefix":
                self.checkpoint_prefix = l[1]
            elif l[0] == "new_dim":
                self.new_dim = int(l[1])
            elif l[0] == "seed":
                self.seed = int(l[1])
            elif l[0] == "anchor_thresh":
                self.anchor_thresh = int(l[1])
            elif l[0] == "top_words":
                self.top_words = int(l[1])

#parse input args
if len(sys.argv) > 6:
    infile = sys.argv[1]
    settings_file = sys.argv[2]
    vocab_file = sys.argv[3]
    K = int(sys.argv[4])
    loss = sys.argv[5]
    outfile = sys.argv[6]

else:
    print "usage: ./learn_topics_file.py word_doc_matrix settings_file vocab_file K loss output_filename"
    # python get_anchors/learn_topics_file.py result25/test_data_1.mat get_anchors/settings.example indices.txt 5 L2 result25/result\_out.5
    print "for more info see readme.txt"
    sys.exit()

params = Params(settings_file)
params.dictionary_file = vocab_file

vocab = file(vocab_file).read().strip().split()

# load files and info
# infile = "../result25/test_data_1.mat"
mat = scipy.io.loadmat(infile)

Q_emp = mat['Q_emp']
var_analytical = mat['var_analytical']
Q = mat['Q']
A = mat['A']

M = Q_emp
K = 5

# anchor_thresh = 2
# outfile = 
# loss = 

# find candidate anchors
candidate_anchors = [i for i in xrange(M.shape[0])]
# for i in xrange(M.shape[0]):
# 	if len(np.nonzero(M[i,:])[1]) > anchor_thresh:
# 		candidate_anchors.append(i)

print len(candidate_anchors), "candidates"

# forms Q matrix from document-word matrix
print "Q sum is", Q_emp.sum()
print "done reading documents"

# row normalize Q and var
Q_bar = np.zeros((M.shape))
var = np.zeros((M.shape))
row_sums = Q_emp.sum(1)
for i in xrange(len(Q_emp[:,0])):
	Q_bar[i,:] = Q_emp[i,:]/float(row_sums[i])
	var[i,:] = var_analytical[i,:]/(float(row_sums[i])**2)


# find anchors
(anchors, anchor_indices) = gs.Projection_Find(Q_bar, K, candidate_anchors, var)
anchor_indices = [int(a) for a in anchor_indices]
print "anchors are:"
for i, a in enumerate(anchors):
    print i, vocab[int(a)]

# recover topics
A, topic_likelihoods, R = do_recovery(Q_emp, anchors, loss, params)
print "done recovering"

np.savetxt(outfile+".A", A)
np.savetxt(outfile+".topic_likelihoods", topic_likelihoods)
np.savetxt(outfile+".R", R)
# np.savetxt(outfile+".Q", Q)

#display
f = file(outfile+".topwords", 'w')
for k in xrange(K):
    mask = A[:, k] > 0.01
    topwords = [ x for x in np.argsort(A[:, k]) if mask[x] ][::-1]
    # topwords = np.argsort(A[:, k])[-params.top_words:][::-1]
    # print params.top_words
    # print 'npargsort', A[:, k]
    print vocab[anchors[k]], ':',
    print >>f, vocab[anchors[k]], ':',
    for w in topwords:
        print vocab[w],
        print >>f, vocab[w],
    print ""
    print >>f, ""

