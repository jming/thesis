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

def get_cui_trie(filename):

	# load_chv
	column_names = ['cui', 'term', 'chv_pref_name']
	# cui_df = pd.read_csv(filename, sep='\t', names=column_names, usecols=[0,1,2])
	cui_df = pd.read_csv(filename, names=column_names, usecols=[0,1,2])

	# build trie
	cui_trie = make_trie(cui_df)

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

def make_trie(df):

	root = {}
	for i,row in df.iterrows():
		current_dict =root
		if type(row['term']) is str:
			for letter in row['term']:
				current_dict = current_dict.setdefault(letter, {})
		current_dict = current_dict.setdefault(_end, row['cui'])
	return root


# def in_trie(trie, word):
# 	current_dict = trie
# 	for letter in word:
# 		if letter in current_dict:
# 			current_dict = current_dict[letter]
# 		else:
# 			return -1
# 	else:
# 		if _end in current_dict:
# 			return current_dict[_end]
# 		else:
# 			return -1

def in_trie(trie, word):

	matches = []

	current_dict = trie

	for i,letter in enumerate(word):

		# print i, letter, word

		if letter in current_dict:
			# print 'in dict'
			current_dict = current_dict[letter]
		else:
			current_dict = trie

		if _end in current_dict:
		 # and word[i+1] == ' ' or i == len(word) - 1:
		 	if i < len(word) - 1 and word[i+1] == ' ':
				# print 'end in dict'
				matches.append(current_dict[_end])

	if _end in current_dict:
		# print 'final end in dict'
		matches.append(current_dict[_end])

	# print 'matches', matches
	return matches




# def in_trie(trie, word):

# 	matches = []
# 	is_passed = False
# 	passed_letters = -1
# 	is_space = False
# 	current_dict = trie

# 	for i, letter in enumerate(word):

# 		is_next = False

# 		# print i, letter, word

# 		if letter == ' ':
# 			is_space = True

# 		if _end in current_dict:
# 			# print 'end in dict'
# 			if is_space:
# 				matches.append(current_dict[_end])
# 				passed_letters = i
# 				is_next = True

# 		if letter in current_dict:
# 			# print 'letter in dict'
# 			current_dict = current_dict[letter]
# 			is_next = True

# 		if is_next and is_space:
# 			passed_letters = i+1

# 		if not is_next and is_space:
# 			# print 'not is_next'
# 			if is_space and passed_letters == -1 or passed_letters == 0:
# 				passed_letters = i+1
# 			matches += in_trie(trie, word[passed_letters:])
# 			break

# 	if _end in current_dict:
# 		matches.append(current_dict[_end])

# 	# print matches
# 	return list(set(matches))

def write_list(filename, lst):

	with open(filename, 'a') as f:
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
		post_split = post.split()
		# for word in post_split:
		# 	cui = in_trie(cui_trie, word)
		# 	if cui > 0:
		cuis = in_trie(cui_trie, post)
		print 'cuis', cuis
		
		if cuis:
			for cui in cuis:
				cui_int = int(cui[1:])
				try:
					cui_rows[cui_int] += 1.
				except KeyError:
					cui_rows[cui_int] = 1.
				cui_counter[i, cui_int] = 1.

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

	else:
		print 'usage ./getq.py post_infile cui_infile matrix_outfile cui_outfile'
		sys.exit()

	# get posts
	print 'getting all posts', time.time()
	all_posts = [line.strip() for line in open(post_infile)]
	print 'number of posts', len(all_posts)

	# get chv trie
	print 'getting cui trie', time.time()
	cuis_list, cui_trie, cui_dict = get_cui_trie(cui_infile)
	print 'number of cuis', len(cuis_list)

	# print 'writing cuis list', time.time()
	# write_list(cui_outfile, cuis_list)

	# print 'writing cuis dict', time.time()
	# write_list('cui_dict.txt', cui_dict)

	# get sums
	print 'getting cui counter', time.time()
	cui_rows, cui_counter = get_cui_counter(cui_trie, all_posts, cuis_list)
	print 'cui_counter', cui_counter

	# store cui counter
	# print 'writing cui counter', time.time()
	# scipy.io.savemat(matrix_outfile, {'M': cui_counter.transpose()}, oned_as='column')

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


