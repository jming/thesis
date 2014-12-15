#!/bin/bash

echo 'start pipeline'

echo 'processing posts'
# python get_q/getq.py all_posts.txt chv.tsv cui_counter.mat cui_list.txt
python get_q/getq.py get_q/test.txt get_q/chv_small.csv cui_counter.mat cui_list.txt

echo 'starting words recovery'
for loss in L2
do
	for K in 20 50 100
	do
		echo 'learning with nonnegative recover method using $loss loss...'
		python get_anchors/learn_topics.py cui_counter.mat get_anchors/settings.example cui_list.txt $K $loss result\_out.$K
	done
done
