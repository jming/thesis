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
# import scipy.sparse as sparse
# import scipy.io as sio
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

def get_cui_sum_matrix(cui_counter):
	return cui_counter.transpose() * cui_counter

def get_cui_prob_matrix(cui_rows, cui_sums, cui_counter):

	cui_sums = cui_sums.todok()

	nonzero = cui_sums.nonzero()
	nonzero0 = nonzero[0]
	nonzero1 = nonzero[1]

	print 'placing divisions', time.time()

	nonzero = zip(nonzero0, nonzero1)
	for nz1,nz2 in nonzero:
		cui_sums[nz1,nz2] = cui_sums[nz1,nz2] / cui_rows[nz1]

	return cui_sums

def write_matrix(filename,matrix,csv=False):

	with open(filename, 'wb') as f:
		pickle.dump(matrix,f)

def main():

	print 'getting all posts', time.time()
	all_posts = exploration.get_lines('all_posts.txt')

	print 'getting chv trie', time.time()
	cuis_list,chv_trie = get_chv_trie('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

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
	write_matrix('cui_matrix.pickle', cui_matrix)


main()