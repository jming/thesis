#!/bin/bash
echo 'start autism'

# echo 'downloading posts'
# echo 'preprocessing, translate from docword.txt to scipy format'
# python uci_to_scipy.py ../all_posts.txt all_posts.mat

echo 'preprocessing, removing rare words and stop words'
python truncate_vocabulary.py ../autism_words_T.mat ../autism_vocab.txt 50

for loss in L2
do
	for K in 20 50 100
	do
		echo "learning with nonnegative recover method using $loss loss..."
		python learn_topics.py ../autism_words_T.mat.trunc.mat settings.example ../autism_vocab.txt.trunc $K $loss autism\_out.$K
	done
done

