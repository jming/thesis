#!/bin/bash

echo 'start pipeline'

echo 'processing posts'
python getq.py

for loss in L2
do
	for K in 20 50 100
	do
		echo 'learning with nonnegative recover method using $loss loss...'
		python learn_topics.py ../cui_counter.mat settings.example ../cui_list.txt $K $loss cui\_out.$K