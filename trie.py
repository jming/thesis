import pandas as pd
_end = '_end_'

# def load_chv(file_name):
# 	return chv_df = pd.read_csv(file_name, sep='\t', names=column_names, usecols=[0,1,2])

def make_trie(df):
	root = {}
	for i,row in df.get_group(1).iterrows():
	# for word in words:
		# print row
		# print row['term']
		current_dict = root
		# print row['term']
		# if row['term'] == 'nan' or row['term'] == float('nan'):
		if type(row['term']) is str:
			# print 'derp'
			# row['term'] = ['n','a','n']
			for letter in row['term']:
				current_dict = current_dict.setdefault(letter, {})
		current_dict = current_dict.setdefault(_end, row['cui'])
		# break
	return root

# print make_trie(['foo', 'bar', 'baz', 'barz'])

def in_trie(trie, word):
	current_dict = trie
	for letter in word:
		if letter in current_dict:
			current_dict = current_dict[letter]
		else:
			return -1
	else:
		if _end in current_dict:
			return current_dict[_end]
		else:
			return -1

# t = make_trie(['foo', 'bar', 'baz', 'barz'])
# print t
# print in_trie(t, 'bar')