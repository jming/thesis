import pandas as pd
import time
import cPickle as pickle
from scipy.sparse import *
from scipy import *
import scipy.io
import numpy as np

# get Q matrix

MAX_CUI = 1321801
_end = '_end_'


######################################

def get_cui_trie(filename):

	# load_chv
	column_names = ['cui', 'term', 'chv_pref_name']
	cui_df = pd.read_csv(filename, sep='\t', names=column_names, usecols=[0,1,2])
	# cui_df = pd.read_csv(filename, names=column_names, usecols=[0,1,2])

	# build trie
	cui_trie = make_trie(cui_df)

	# get cui list
	cuis_list = list(set(sorted(cui_df['cui'])))

	return (cuis_list, cui_trie)

def make_trie(df):

	root = {}
	for i,row in df.iterrows():
		current_dict =root
		if type(row['term']) is str:
			for letter in row['term']:
				current_dict = current_dict.setdefault(letter, {})
		current_dict = current_dict.setdefault(_end, row['cui'])
	return root

def in_trie(trie, word):

	curr_matches = []
	matches = []

	current_dict = trie
	for i,letter in enumerate(word):

		# print i, letter, current_dict
		
		is_next = False

		if _end in current_dict:
			# print 'end in current_dict'
			curr_matches.append(current_dict[_end])
			is_next = True
			#  this needs to be handled differently

		if letter in current_dict:
			# print 'letter in current_dict'
			current_dict = current_dict[letter]
			is_next = True

		# print is_next 

		if is_next and letter == ' ':
			# print 'letter is space'
			matches += in_trie(trie, word[i+1:])

		if not is_next:
			# print 'not is_next'
			matches += in_trie(trie, word[i+1:])
			matches += curr_matches
			break

	if _end in current_dict:
		matches.append(current_dict[_end])

	return list(set(matches))


	# else:
	# 	if _end in current_dict:
	# 		return current_dict[_end]
	# 	else:
	# 		return -1

def write_list(filename, lst):

	with open(filename, 'a') as f:
		for l in lst:
			try:
				f.write('%s\n' % l)
			except:
				f.write(' \n')

def get_cui_counter(cui_trie, posts, cuis):

	N = len(posts)
	M = MAX_CUI+1
	cui_rows = {}

	cui_counter = dok_matrix((N,M), dtype=float32)

	for i,post in enumerate(posts):
		# post_split = post.split()
		# for word in post_split:
			# cui = in_trie(cui_trie, word)
			# if cui > 0:
		cuis = in_trie(cui_trie, post)
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

# trie = {'a':{'b':{'s':{'_end_':'1'}, 'o':{'u':{'t':{'_end_':'2', ' ':{'y':{'o':{'u':{'_end_':'3'}}}}}}}}}}
# print in_trie(trie, 'abs about')
# print in_trie(trie, 'i am crazy about abs')
# print in_trie(trie, 'i am crazy about you')
# print in_trie(trie, 'abs i am')
# print in_trie(trie, 'about you')
# print in_trie(trie, 'abolution')
# print in_trie(trie, 'i am crazy about you and about abs')
# print in_trie(trie, 'i am crazy about you and abs')
# ISSUE with _end_ being the only thing in the dictionary

# if __name__ == '__main__':

# 	# get posts
# 	print 'getting all posts', time.time()
# 	all_posts = [line.strip() for line in open('test.txt')]
# 	print 'number of posts', len(all_posts)

# 	# get chv trie
# 	print 'getting cui trie', time.time()
# 	cuis_list, cui_trie = get_cui_trie('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')
# 	print 'number of cuis', len(cuis_list)

# 	print 'writing cuis list', time.time()
# 	write_list('cui_list.txt', cuis_list)

# 	# get sums
# 	print 'getting cui counter', time.time()
# 	cui_rows, cui_counter = get_cui_counter(cui_trie, all_posts, cuis_list)

# 	# store cui counter
# 	print 'writing cui counter', time.time()
# 	scipy.io.savemat('cui_counter.mat', {'M': cui_counter.transpose().tolil()}, oned_as='column')

# 	# # get cui cooccurrence matrix
# 	# print 'getting cooccurrence', time.time()
# 	# cui_sums = cui_counter.transpose() * cui_counter

# 	# # store cui cooccur
# 	# print 'writing cui cooccurrence', time.time()
# 	# write_matrix('cui_cooccur.pickle', cui_sums)

# 	# # normalize matrix
# 	# print 'normalizing matrix', time.time()
# 	# cui_matrix = normalize_matrix(cui_rows, cui_sums, cui_counter)

# 	# # store normalized matrix
# 	# print 'writing normalized matrix', time.time()
# 	# write_matrix('cui_matrix.pickle', cui_matrix)


