#!/bin/bash

echo 'start pipeline'

echo 'processing posts'
# python get_q/getq.py all_posts.txt chv.tsv cui_counter.mat cui_list.txt
cd get_q
ls 
python getq.py test.txt chv_small.csv ../cui_counter.mat ../cui_list.txt
cd ..

for loss in L2
do
	for K in 20 50 100
	do
		echo 'learning with nonnegative recover method using $loss loss...'
		python anchor_words_recovery/learn_topics.py cui_counter.mat anchor_words_recovery/settings.example cui_list.txt $K $loss result\_out.$K