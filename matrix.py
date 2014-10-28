import exploration
import chv
import trie
import collections
import itertools
import csv
import time
import sys
# import pandas as pd
import ast
from scipy.sparse import *
from scipy import *
import numpy as np
import cPickle as pickle



MAX_CUI = 1321801

def get_chv_trie(file_name, limit=None):
	chv_df = chv.load_chv(file_name, limit)
	chv_trie = trie.make_trie(chv_df)
	cuis = chv_df['cui']
	cuis_list = list(set(sorted(list(cuis.get_group(1)))))

	return (cuis_list,chv_trie)

# def get_all_cuis(chv_trie, posts):

# 	cui_counter = {}

# 	for i,post in enumerate(posts):
# 		print 'post', i, time.time()
# 		post_split = post.split()
# 		for word in post_split:
# 			cui = trie.in_trie(chv_trie, word)
# 			if cui > 0:
# 				try:
# 					cui_counter[cui].append(i)
# 				except KeyError:
# 					cui_counter[cui] = [i]

# 	return cui_counter

def get_cui_counter_matrix(chv_trie, posts, cuis):

	N = len(posts)
	# M = len(cuis)
	M = MAX_CUI+1
	cui_rows = {}

	cui_counter = dok_matrix((N,M), dtype=float32)

	for i,post in enumerate(posts):
		post_split = post.split()
		for word in post_split:
			cui = trie.in_trie(chv_trie, word)
			if cui > 0:
				cui_int = int(cui[1:])
				# print cui_int
				try:
					cui_rows[cui_int] += 1.
				except KeyError:
					cui_rows[cui_int] = 1.
				cui_counter[i, int(cui[1:])] = 1.

	return cui_rows,cui_counter

# def get_cui_from_csv(file_name):
# 	csv.field_size_limit(sys.maxsize)
# 	cui_counter = {}
# 	with open(file_name, 'rb') as f:
# 		reader = csv.reader(f)
# 		for row in reader:
# 			cui_counter[row[0]] = row[1]
# 	return cui_counter

# def clean_cuis(cuis, threshold):
# 	delete = []
# 	for cui in cuis.keys():
# 		if len(cuis[cui]) < threshold:
# 			# print 'deleting!'
# 			# print cui
# 			del cuis[cui]
# 	return cuis

# def string_to_list(string):
# 	return ast.literal_eval(string)

def get_cui_sum_matrix(cui_counter):
	return cui_counter.transpose() * cui_counter

def get_cui_prob_matrix(cui_rows, cui_sums, cui_counter):

	cui_sums = cui_sums.todok()

	nonzero = cui_sums.nonzero()
	nonzero0 = nonzero[0]
	nonzero1 = nonzero[1]

	# print 'getting sums', time.time()
	# col_sums = {}
	# # print 
	# nonzero0_set = set(nonzero0)
	# print len(nonzero0_set)
	# for nz in nonzero0_set:
	# 	col_sums[nz] = cui_counter.getcol(nz).sum()

	print 'placing divisions', time.time()

	nonzero = zip(nonzero0, nonzero1)
	# print len(nonzero)
	# print nonzero
	for nz1,nz2 in nonzero:
		# print nz1,nz2
		# col_sum = cui_counter.getcol(nz1).sum()
		# print col_sum
		# print cui_counter.getcol(nz1)
		cui_sums[nz1,nz2] = cui_sums[nz1,nz2] / cui_rows[nz1]

	# print nonzero.T
	return cui_sums


# def get_cui_prob(cui1, cui2):
# 	same = set(string_to_list(cui1)) & set(string_to_list(cui2))
# 	return (float(len(same)) / len(cui1), float(len(same)) / len(cui2))

# def get_all_prob(cuis):

# 	results = {}
# 	for cui1,cui2 in itertools.combinations(cuis.keys(), 2):
		
# 		p1,p2 = get_cui_prob(cuis[cui1], cuis[cui2])
# 		results[(cui2,cui1)] = p1
# 		results[(cui1,cui2)] = p2

# 	return results

# def get_prob_df(probs):
# 	data = map(list, zip(*probs.keys()) + [probs.values()])
# 	df = pd.DataFrame(zip(*data)).set_index([0,1])[2].unstack()
# 	return df.combine_first(df.T).fillna(0)

# def write_list(info, out_file):

# 	with open(out_file, 'wb') as f:
# 		writer = csv.writer(f)
# 		writer.writerows(info)

# def write_dict(info, out_file):
# 	with open(out_file, 'wb') as f:
# 		writer = csv.writer(f)
# 		for key,value in info.items():
# 			writer.writerow([key, value])

def write_matrix(filename,matrix,csv=False):
	if csv:
		# print 'matrix', matrix
		matrix_array = matrix.toarray()
		# print 'matrix arra', matrix_array
		np.savetxt(filename, matrix_array, delimiter=',')
	else:
		with open(filename, 'wb') as f:
			pickle.dump(matrix, f, pickle.HIGHEST_PROTOCOL)

def main():

	print 'getting all posts', time.time()
	all_posts = exploration.get_lines('all_posts.txt')
	# print len(all_posts)

	print 'getting chv trie', time.time()
	cuis_list,chv_trie = get_chv_trie('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

	# print cuis_list[-10:]
	# print len(cuis_list)
	# print sorted(cuis_list)[-10:]

	print 'getting cuis', time.time()
	cui_rows,cui_counter = get_cui_counter_matrix(chv_trie, all_posts, cuis_list)
	print cui_counter

	print 'getting sums', time.time()
	cui_sums = get_cui_sum_matrix(cui_counter)
	print cui_sums

	print 'getting probs', time.time()
	cui_matrix = get_cui_prob_matrix(cui_rows, cui_sums, cui_counter)
	print cui_matrix

	print 'writing csv', time.time()
	write_matrix('cui_matrix.dat', cui_matrix)


main()