_end = '_end_'

# def load_chv()

def make_trie(words):
	root = {}
	for word in words:
		current_dict = root
		for letter in word:
			current_dict = current_dict.setdefault(letter, {})
		current_dict = current_dict.setdefault(_end, 12)
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

t = make_trie(['foo', 'bar', 'baz', 'barz'])
print t
print in_trie(t, 'bar')