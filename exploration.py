def get_lines(filename):
	# print 'getting_lines'
	return [line.strip() for line in open(filename)]

def get_posts(posts, ns):
	return [posts[n] for n in ns]

def get_posts_with(posts, words):
	posts_with = []
	for i,post in enumerate(posts):
		for word in words:
			if word in post:
				posts_with.append(i)
	return list(set(posts_with))

def get_probability(posts, word):
	num_posts = float(len(posts))
	posts_with_word = get_posts_with(posts, word)
	num_word = float(len(posts_with_word))
	return num_word / num_posts

def get_conditional_probability(posts, word1, word2):

	num_posts = float(len(posts))

	posts_with_word1 = get_posts_with(posts, word1)
	num_word1 = float(len(posts_with_word1))
	p_word1 = num_word1 / num_posts
	posts_with_word1 = get_posts(posts, posts_with_word1)
	# print 'num_word1', num_word1
	
	posts_with_word1_word2 = get_posts_with(posts_with_word1, word2)
	num_word1_word2 = float(len(posts_with_word1_word2))
	p_word1_word2 = num_word1_word2 / num_posts
	# print 'num_word1_word2', num_word1_word2

	return p_word1_word2 / p_word1

def naive():

	all_posts = get_lines('all_posts.txt')

	print 'probability'
	print 'epilepsy', get_probability(all_posts, ['epilepsy'])
	print 'adhd', get_probability(all_posts, ['adhd', 'add'])
	print 'schizophrenia', get_probability(all_posts, ['schizophrenia', 'schizophrenic'])
	print 'spd', get_probability(all_posts, ['spd', 'sensory'])
	print 'aspergers', get_probability(all_posts, ['aspergers', 'asperger'])

	print 'conditional probability'
	print 'epilepsy, seizure', get_conditional_probability(all_posts, ['epilepsy'], ['seizure', 'seizures'])
	print 'adhd, schizophrenia', get_conditional_probability(all_posts, ['adhd', 'add'], ['schizophrenia', 'schizophrenic'])
	print 'adhd, ocd', get_conditional_probability(all_posts, ['adhd', 'add'], ['ocd', 'obsessive'])

def naive_phrase():

	all_posts = get_lines('all_posts.txt')

	print 'probability'
	print 'epilepsy', get_probability(all_posts, ['epilepsy'])
	print 'adhd', get_probability(all_posts, ['adhd', 'add', 'attention deficit', 'attention-deficit', 'hyperactivity'])
	print 'schizophrenia', get_probability(all_posts, ['schizophrenia', 'schizophrenic'])
	print 'spd', get_probability(all_posts, ['spd', 'sensory', 'sensory processing'])
	print 'aspergers', get_probability(all_posts, ['aspergers', 'asperger'])

	print 'conditional probability'
	print 'epilepsy, seizure', get_conditional_probability(all_posts, ['epilepsy'], ['seizure', 'seizures'])
	print 'adhd, schizophrenia', get_conditional_probability(all_posts, ['adhd', 'add'], ['schizophrenia', 'schizophrenic'])
	print 'adhd, ocd', get_conditional_probability(all_posts, ['adhd', 'add', 'attention deficit', 'attention-deficit', 'hyperactivity'], ['ocd', 'obsessive', 'obsessive compulsive'])

# naive_phrase()

# def store_chv():

	

