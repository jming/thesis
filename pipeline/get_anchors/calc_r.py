from Q_matrix import generate_Q_matrix 

import numpy as np

import scipy.io as sio

filename = '../result10/'

for N in ['20', '50', '100']:

	filenamea = filename+'result_out.'+N+'.A'
	A = np.loadtxt(filenamea)

	filenameq = filename+'cui_counter.mat.trunc.mat'
	Q = generate_Q_matrix(sio.loadmat(filenameq)['M'])

	# filenameq = filename+'result_out.'+N+'.Q'
	# Q = np.loadtxt(filenameq)

	# print 'Q shape', Q.shape
	# print Q

	A_tall = np.linalg.pinv(A)

	# print 'A_tall shape', A_tall.shape
	# print A_tall

	R = A_tall.dot(Q).dot(A_tall.transpose())

	np.savetxt(filename+'result_out.'+N+'.R', R)
