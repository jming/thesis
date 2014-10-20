import exploration
import chv
import trie
import collections
import itertools
import csv
import time
<<<<<<< HEAD
import sys

ALL_POSTS = 144368

# def get_all_chv(posts):
# def get_all_cuis(posts):

# 	print 'getting all'
# 	# all_chv = []
# 	cui_counter = {}

# 	chv_df = chv.load_chv('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

# 	for i,post in enumerate(posts):
# 		print 'post', i
# 		post_split = post.split()
# 		cuis = chv.find_in_chv(post_split, chv_df)
# 		for cui in cuis:
# 			try:
# 				cui_counter[cui].append(i)
# 			except KeyError:
# 				cui_counter[cui] = [i]
# 			# cui_counter[cui] += 1
# 		# all_chv.append([i, post, cuis])

# 	# return all_chv
# 	return cui_counter

def get_chv_trie(file_name):
	# print 'getting chv trie', time.time()
	chv_df = chv.load_chv(file_name)
	chv_trie = trie.make_trie(chv_df)

	return chv_trie


=======

# def get_all_chv(posts):
# def get_all_cuis(posts):

# 	print 'getting all'
# 	# all_chv = []
# 	cui_counter = {}

# 	chv_df = chv.load_chv('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

# 	for i,post in enumerate(posts):
# 		print 'post', i
# 		post_split = post.split()
# 		cuis = chv.find_in_chv(post_split, chv_df)
# 		for cui in cuis:
# 			try:
# 				cui_counter[cui].append(i)
# 			except KeyError:
# 				cui_counter[cui] = [i]
# 			# cui_counter[cui] += 1
# 		# all_chv.append([i, post, cuis])

# 	# return all_chv
# 	return cui_counter

def get_chv_trie(file_name):
	# print 'getting chv trie', time.time()
	chv_df = chv.load_chv(file_name)
	chv_trie = trie.make_trie(chv_df)

	return chv_trie


>>>>>>> 5fbf8e5c8b5b2e25c8480e4a52f2a04cf7a268a1
def get_all_cuis(chv_trie, posts):

	# print 'getting all', time.time()
	cui_counter = {}

	for i,post in enumerate(posts):
		print 'post', i, time.time()
		post_split = post.split()
		for word in post_split:
			cui = trie.in_trie(chv_trie, word)
			if cui > 0:
				try:
					cui_counter[cui].append(i)
				except KeyError:
					cui_counter[cui] = [i]

	return cui_counter

def get_cui_from_csv(file_name):
	csv.field_size_limit(sys.maxsize)
	cui_counter = {}
	with open(file_name, 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			cui_counter[row[0]] = row[1]
	return cui_counter

def clean_cuis(cuis, threshold):
	delete = []
	for cui in cuis.keys():
		if len(cuis[cui]) < threshold:
			# print 'deleting!'
			# print cui
			del cuis[cui]
	return cuis

def get_cui_prob(cui1, cui2):
	same = set(cui1) & set(cui2)
	return (float(len(same)) / len(cui1), float(len(same)) / len(cui2))

def get_all_prob(cuis):

	# print 'getting all prob'

	# with open('all_prob.csv', 'wb') as f:
		# writer = csv.writer(f)

	results = []
	for cui1,cui2 in itertools.combinations(cuis.keys(), 2):
		print cui1,cui2
		# results[(cui1,cui2)] = get_cui_prob(cuis[cui1], cuis[cui2], num_posts)
		# results.append([cui1, cui2, get_cui_prob(cuis[cui1], cuis[cui2], num_posts)])
		p1,p2 = get_cui_prob(cuis[cui1], cuis[cui2])
		# results.append([cui1, cui2, get_cui_prob(cuis[cui1], cuis[cui2], num_posts)])
		results.append([cui2, cui1, p1])
		results.append([cui1, cui2, p2])

			# writer.writerows([cui1, cui2, prob])
	return results

def write_list(info, out_file):

	with open(out_file, 'wb') as f:
		writer = csv.writer(f)
		writer.writerows(info)

def write_dict(info, out_file):
	with open(out_file, 'wb') as f:
		writer = csv.writer(f)
		for key,value in info.items():
			writer.writerow([key, value])

def incremental_write(chv_trie, posts, n, incr):

	for i in range(0,n,incr):
		end = min(i+incr, n)
		cui_counter = get_all_cuis(chv_trie, posts[i:end])
		probs = get_all_prob

def main():

	# print 'getting all posts', time.time()
	# all_posts = exploration.get_lines('all_posts.txt')
	# print len(all_posts)

	# print 'getting chv trie', time.time()
	# chv_trie = get_chv_trie('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

	# print 'testing chv trie', time.time()

	# print trie.in_trie(chv_trie, 'abdominal')
	# print trie.in_trie(chv_trie, 'epilepsy')
	# print trie.in_trie(chv_trie, 'autism')
	# print trie.in_trie(chv_trie, 'joy')

	# print get_all_cuis(chv_trie, ['abdnominal epilepsy autism joy'])

	# all_chv = get_all_chv(all_posts)
	# print 'getting cuis', time.time()
	# cui_counter = get_all_cuis(chv_trie, all_posts)
	# print cui_counter

	# print 'writing cuis', time.time()
	# write_dict(cui_counter, 'cui_counter.csv')

	print 'getting cuis', time.time()
	cui_counter = get_cui_from_csv('cui_counter.csv')

	# print cui_counter

	print 'cleaning cuis', time.time()
	cui_counter_cleaned = clean_cuis(cui_counter, 100)
	# print len(cui_counter.keys()), len(cui_counter_cleaned.keys())

	print 'getting probs', time.time()
	all_prob = get_all_prob(cui_counter_cleaned)
	# # print all_prob

	print 'writing probs', time.time()
	write_list(all_prob, 'all_prob.csv')

	# print all_prob

main()