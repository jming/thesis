#!/usr/bin/env python

import pandas as pd
import time
import cPickle as pickle
from scipy.sparse import *
from scipy import *
import scipy.io
import numpy as np
import sys

# get Q matrix

MAX_CUI = 1321801
_end = '_end_'


######################################

def get_cui_trie(filename, stopwords):

	# load_chv
	column_names = ['cui', 'term', 'chv_pref_name']
	cui_df = pd.read_csv(filename, sep='\t', names=column_names, usecols=[0,1,2])
	# cui_df = pd.read_csv(filename, names=column_names, usecols=[0,1,2])
	# cui_df = pd.read_csv(filename)
	stopwords_list = get_stopwords_list(stopwords)
	# print stopwords_list

	# build trie
	cui_trie = make_trie(cui_df, stopwords_list)

	# get cui list
	cui_list = [' ' for x in range(MAX_CUI+1)]
	cui_dict = []

	cui_sort = cui_df.sort('cui')
	cui_grouped = cui_sort.groupby('cui')
	for name,group in cui_grouped:
		cui_dict.append(name + '\t' + list(group['chv_pref_name'])[0])
		idx = int(name[1:])
		if idx < MAX_CUI+1:
			cui_list[idx] = name
	# cuis_list0 = list(set(sorted(cui_df['cui'])))

	return (cui_list, cui_trie, cui_dict)

def get_stopwords_list(f):

	print 'getting stopwords list'

	with open(f, "r") as fi:
		return [r[:-1] for r in fi]

def make_trie(df, stopwords_list):

	root = {}
	for i,row in df.iterrows():
		current_dict =root
		term = row['term']
		# print term
		if type(term) is str and term not in stopwords_list:
			# print 'in!'
			for letter in term:
				current_dict = current_dict.setdefault(letter, {})
		current_dict = current_dict.setdefault(_end, row['cui'])
	return root

def in_trie(trie, word):

	matches = []

	current_dict = trie
	passed_index = -1

	i = 0

	while i < len(word):

		letter = word[i]

		# if letter matches, move to next dictionary
		if letter in current_dict:
			current_dict = current_dict[letter]
			if not letter.isalpha():
				passed_index = i
		else:
			
			current_dict = trie

			# if passed a space, start over at last index after space
			if passed_index > 0:
				i = passed_index
				passed_index = -1

		# if end of word is found, append
		if _end in current_dict:
		 	if i < len(word) - 1 and not word[i+1].isalpha():
				matches.append(current_dict[_end])

		i += 1

	# if end of word is found, append
	if _end in current_dict:
		matches.append(current_dict[_end])

	return list(set(matches))

def write_list(filename, lst):

	with open(filename, 'w') as f:
		for l in lst:
			try:
				f.write('%s\n' % l)
			except:
				f.write(' \n')

def get_cui_counter(cui_trie, posts, cuis):

	N = len(posts)
	M = MAX_CUI + 1
	cui_rows = {}

	cui_counter = dok_matrix((N,M), dtype=float32)

	for i,post in enumerate(posts):
		print 'doing post', i, 'length', len(post), time.time()

		# get cuis from post
		cuis = in_trie(cui_trie, post)
		
		if cuis and len(cuis) > 1:
			for cui in cuis:
				cui_int = int(cui[1:])

				# add to row count
				try:
					cui_rows[cui_int] += 1.
				except KeyError:
					cui_rows[cui_int] = 1.

				# add to post-concept count matrix
				cui_counter[i, cui_int] += 1.

	return cui_rows, cui_counter

def normalize_matrix(cui_rows, cui_sums, cui_counter):

	cui_sums = cui_sums.todok()

	nonzero = cui_sums.nonzero()
	nonzero0 = nonzero[0]
	nonzero1 = nonzero[1]

	nonzero = zip(nonzero0, nonzero1)
	for nz1, nz2 in nonzero:
		cui_sums[nz1, nz2] = cui_sums[nz1, nz2] / cui_rows[nz1]

	return cui_sums


def write_matrix(filename, matrix, csv=False):

	with open(filename, 'wb') as f:
		pickle.dump(matrix, f)

##########################################



if __name__ == '__main__':

	if len(sys.argv) > 4:

		post_infile = sys.argv[1]
		cui_infile = sys.argv[2]

		matrix_outfile = sys.argv[3]
		cui_outfile = sys.argv[4]

		stopwords = sys.argv[5]

	else:
		print 'usage ./getq.py post_infile cui_infile matrix_outfile cui_outfile stopwords'
		sys.exit()

	# get posts
	print 'getting all posts', time.time()
	all_posts = [line.strip() for line in open(post_infile)]
	print 'number of posts', len(all_posts)

	# get chv trie
	print 'getting cui trie', time.time()
	cuis_list, cui_trie, cui_dict = get_cui_trie(cui_infile, stopwords)
	print 'number of cuis', len(cuis_list)

	print 'writing cuis list', time.time()
	write_list(cui_outfile, cuis_list)

	print 'writing cuis dict', time.time()
	write_list('cui_dict.txt', cui_dict)

	# get sums
	print 'getting cui counter', time.time()
	cui_rows, cui_counter = get_cui_counter(cui_trie, all_posts, cuis_list)
	# print 'cui_counter', cui_counter

	# store cui counter
	print 'writing cui counter', time.time()
	scipy.io.savemat(matrix_outfile, {'M': cui_counter.transpose()}, oned_as='column')

	sys.exit()

	# # get cui cooccurrence matrix
	# print 'getting cooccurrence', time.time()
	# cui_sums = cui_counter.transpose() * cui_counter

	# # store cui cooccur
	# print 'writing cui cooccurrence', time.time()
	# write_matrix('cui_cooccur.pickle', cui_sums)

	# # normalize matrix
	# print 'normalizing matrix', time.time()
	# cui_matrix = normalize_matrix(cui_rows, cui_sums, cui_counter)

	# # store normalized matrix
	# print 'writing normalized matrix', time.time()
	# write_matrix('cui_matrix.pickle', cui_matrix)


