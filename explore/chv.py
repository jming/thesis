import pandas as pd
# from pandas import read_csv

# column_names = ['cui','term','chv_pref_name','umls_pref_name','explanation','umls_pref','chv_pref','disparaged','freq','context','cui_score','combo','combo_notop','chv_stringid','chv_conceptid']
column_names = ['cui', 'term', 'chv_pref_name']

def load_chv(file_name, limit=None):
	chv_df = pd.read_csv(file_name, sep='\t', names=column_names, usecols=[0,1,2])
	if limit:
		chv_df = chv_df[:limit]
	# print chv_df.head()
	chv_df['count'] = chv_df.apply(lambda row: len(str(row['term']).split()), axis=1)
	chv_df_grouped = chv_df.groupby('count')

	return chv_df_grouped

	# print chv_df_grouped.head()

	# for name,group in chv_df_grouped:
	# 	print name, len(group)
	# print chv_df_grouped.get_groups()

# load_chv('CHV_flatfiles_all/CHV_concepts_terms_flatfile_20110204.tsv')

# def load_chv(file_name, limit=None):

def find_in_chv(words, chv):

	matched = []
	potential = []

	for i in range(len(words)):

		# find this (single) word's cui if exists
		cui = get_cui(words[i], chv)
		if cui > 0:
			matched.append(cui)

		# find cui's up to this point
		# for j in range(i, 0, -1):
		# 	for p,pot in enumerate(potential[j-1]):
		# 		# check if this fits the potential
		# 		cui = check_pot(words[j-1:i], chv, pot)
		# 		# if does not fit in this potential
		# 		if cui < 0:
		# 			del potential[j-1][p]
		# 		# if it is this potential
		# 		if cui > 0:
		# 			del potential[j-1][p]
		# 			matched.append(cui)

		# add to potential cui's
		# potential.append(get_potential(words[i], chv))

	return matched

def get_cui(word, chv):

	# check through all single words for match
	# print chv.get_group(1)
	for i,row in chv.get_group(1).iterrows():
		# print row
		if row['term'] == word:
			return row['cui']
	else:
		return -1

# def get_cui_probability():
	

# def check_pot(words, chv, pot):
	
# 	# get words and change to array
# 	pot_word = chv.loc[pot,:]
# 	pot_words = pot_words.split()

# 	# check if words matches up
# 	for i in range(len(words)):
# 		if words[i] != pot_words[i]:
# 			return -1

# 	# if completely matches up, return cui
# 	if len(words) == len(pot_words):
# 		return pot

# 	# otherwise return 0
# 	return 0

# def get_potential(word, chv):

# 	for name,group in chv:
# 		if name != 1:
# 			for row in group:
# 				pass
# 	pass

# 	# return potential cui's associated with this as first word


