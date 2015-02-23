#!/bin/bash

echo 'start pipeline'

N='23'

# echo 'processing posts'
# # python get_q/getq.py all_posts.txt chv.tsv cui_counter.mat cui_list.txt
# # python get_q/getq.py get_q/test.txt get_q/chv_small.csv cui_counter.mat cui_list.txt
# # python get_q/getq.py get_q/test.txt get_q/chv.tsv test_counter.mat test_list.txt
# # python get_q/getq.py get_q/joy_all_posts.txt get_q/chv.tsv cui_counter.mat cui_list.txt
# python get_q/getq.py get_q/joy_all_posts.txt get_q/mrsty_filtered_bdf.csv cui_counter.mat cui_list.txt stopwords.txt


echo 'preprocessing, removing rare words and stop words'
# # # python get_anchors/truncate_vocabulary.py test_counter.mat test_list.txt 50
# python get_anchors/truncate_vocabulary.py cui_counter.mat cui_list.txt 50

echo 'starting words recovery'
for loss in L2
do
	# for K in 5 20 50 100
	for K in 20
	do
		echo 'learning with nonnegative recover method using $loss loss...'
		# python get_anchors/learn_topics.py cui_counter.mat get_anchors/settings.example cui_list.txt $K $loss result\_out.$K
		# python get_anchors/learn_topics.py test_counter.mat.trunc.mat get_anchors/settings.example test_list.txt.trunc $K $loss result\_out.$K
		python get_anchors/learn_topics.py cui_counter.mat.trunc.mat get_anchors/settings.example cui_list.txt.trunc $K $loss result$N/result\_out.$K
		# python get_anchors/learn_topics.py cui_counter.mat.trunc.mat get_anchors/settings.example cui_list.txt.trunc $K $loss result\_out\_rand.$K
		# python get_anchors/learn_topics.py cui_counter.mat.trunc.mat get_anchors/settings.example cui_list.txt.trunc $K $loss result\_out.$K
	done
done

echo 'starting translation'
# for K in 5 20 50 100
for K in 20
do
	echo 'translating $K'
	python get_result/translate.py result$N/result\_out.$K.topwords result$N/result\_out.$K.topwords.translate cui_dict.txt
	# python get_result/translate.py result\_out.$K.topwords result\_out.$K.topwords.translate cui_dict.txt
done