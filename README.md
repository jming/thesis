# \#autism versus 299.0: Topic Model Exploration of Multimodal Autism Data
By Joy Carol Ming 

Though prevalence and awareness for Autism Spectrum Disorder (ASD) has steadily increased,
a true understanding is hard to reach because of the behavior-based nature of the
diagnosis and the heterogeneity of symptoms. Parents and caregivers often informally discuss
symptoms and behaviors they observe from their children with autism through online
medical forums, contrasting the more traditional and structured text of electronic medical
records collected by doctors. We modify an anchor-word driven topic model algorithm originally
proposed by Arora et al. (2012a) to elicit and compare the medical concept topics,
or “themes” from both modes of data: the novel data set of posts from autism-specific online
medical forums and electronic medical records. We present methods to extract relevant
medical concepts from colloquially written forum posts through the use of choice sections
of the consumer health vocabulary and other filtering techniques. In order to account for
the sparsity of concept data, we propose and evaluate a more robust approach to selecting
anchor words that takes into account variance and inclusivity. This approach that combines
concept and anchor words selection seeds the discussion about how unstructured text can
influence and expand understanding of the enigmatic disorder, autism.

Some notable components of this code include the following:
* [**Posts.**](https://github.com/jming/thesis/tree/master/posts) This  includes  both  the  code  for  scraping  the  forums  as  well  as  compressedversions of the raw sources scraped from forums
* [**Exploration.**](https://github.com/jming/thesis/tree/master/results) This includes the code used in data exploration and the visualizations
generated for these explorations and for the paper.
* [**Pipeline.**](https://github.com/jming/thesis/tree/master/pipeline) This includes the code that can be used to run the pipeline. Instructions
for running the pipeline are included on this page and a sample pipeline is included in
pipeline.sh.
* [**Results.**](https://github.com/jming/thesis/tree/master/results) The results section of the code includes the results of running the algorithm
on both the online medical forum and electronic medical records. The textfile
result.txt explains the parameters used to generate each result. The files are named
with the number of anchors and files with *.topwords.translate are the files that
include the anchor words and top words translated from CUIs in a similar format to
those included in the tables throughout the paper.

