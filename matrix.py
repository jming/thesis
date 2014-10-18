import exploration
import chv
import collections
import itertools
import csv

# def get_all_chv(posts):
def get_all_cuis(posts):

	print 'getting all'
	# all_chv = []
	cui_counter = {}

	chv_df = chv.load_chv('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

	for i,post in enumerate(posts):
		print 'post', i
		post_split = post.split()
		cuis = chv.find_in_chv(post_split, chv_df)
		for cui in cuis:
			try:
				cui_counter[cui].append(i)
			except KeyError:
				cui_counter[cui] = [i]
			# cui_counter[cui] += 1
		# all_chv.append([i, post, cuis])

	# return all_chv
	return cui_counter

def get_cui_prob(cui1, cui2, num_posts):
	same = set(cui1) & set(cui2)
	return len(same) / len(cui2)

def get_all_prob(cuis, num_posts):

	print 'getting all prob'

	with open('all_prob.csv', 'wb') as f:
		writer = csv.writer(f)

		results = []
		for cui1,cui2 in itertools.combinations(cuis.keys(), 2):
			# results[(cui1,cui2)] = get_cui_prob(cuis[cui1], cuis[cui2], num_posts)
			# results.append([cui1, cui2, get_cui_prob(cuis[cui1], cuis[cui2], num_posts)])
			prob = get_cui_prob(cuis[cui1], cuis[cui2], num_posts)
			writer.writerows([cui1, cui2, prob])


	# return results

# def write_prob(prob, out_file):
# 	with open(out_file, 'wb') as f:
# 		writer = csv.writer(f)
# 		writer.writerows(prob)

def main():

	all_posts = exploration.get_lines('all_posts.txt')
	# all_chv = get_all_chv(all_posts)
	cui_counter = get_all_cuis(all_posts)
	all_prob = get_all_prob(all_chv, len(all_posts))

	# write_prob(all_prob, 'all_prob.csv')


	# print all_prob

main()