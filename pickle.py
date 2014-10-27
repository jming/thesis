import cPickle as pickle
import scipy
import scipy.sparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

def read_matrix(filename):
	with open(filename, 'rb') as f:
		x = pickle.load(f)
	return x

def write_matrix(filename, matrix):
		matrix_array = matrix.toarray()
		# print 'matrix arra', matrix_array
		np.savetxt(filename, matrix_array, delimiter=',')

def set_plots():

	#colorbrewer2 Dark2 qualitative color table
	dark2_colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
	                (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
	                (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
	                (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
	                (0.4, 0.6509803921568628, 0.11764705882352941),
	                (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
	                (0.6509803921568628, 0.4627450980392157, 0.11372549019607843)]

	rcParams['figure.figsize'] = (10, 6)
	rcParams['figure.dpi'] = 150
	rcParams['axes.color_cycle'] = dark2_colors
	rcParams['lines.linewidth'] = 2
	rcParams['axes.facecolor'] = 'white'
	rcParams['font.size'] = 14
	rcParams['patch.edgecolor'] = 'white'
	rcParams['patch.facecolor'] = dark2_colors[0]
	rcParams['font.family'] = 'StixGeneral'

def plot_array(array):

	dims = np.arange(500, 1500, 20)

	plt.figure()
	plt.plot(dims, array)
	plt.show()


def main():

	matrix = read_matrix('cui_matrix.dat')
	write_matrix('cui_matrix.csv', matrix)

	u,s,vt = scipy.sparse.linalg.svds(matrix)
	print s
	plot_array(s)




# main()