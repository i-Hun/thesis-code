# -*- coding: utf-8 -*-
from analysis import LDA, get_dictionary, get_corpus
import random
import matplotlib.pyplot as plt
import logging
import collections
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)
import numpy as np
import pandas as pd
from gensim import models

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)
lda = LDA(dictionary, corpus, 20, str(20) + "topics")
test_corpus = corpus[1:200]
number_of_words = sum(cnt for document in test_corpus for _, cnt in document)


print number_of_words
perplex = lda.bound(test_corpus)
per_word_perplex = np.exp2(-perplex / number_of_words)
log_perplex = lda.log_perplexity(corpus[1:200], len(corpus))
print perplex, per_word_perplex
print log_perplex, np.exp2(-log_perplex)
# Обычный LDA
# for i in range(100, 101, 1):
#     lda = LDA(dictionary, corpus, i, str(i) + "topics")
# for i, topic in enumerate(lda.show_topics(num_topics=lda.num_topics, num_words=20)):
#     print i+1, topic

#hLDA
# hlda = hLDA(dictionary, corpus)
# for i, topic in enumerate(hlda.show_topics(topics=-1)):
#     print i+1, topic

#MALLET
# for num_topics in range(60, 65, 10):
#     model = models.LdaMallet('~/mallet-2.0.7/bin/mallet', corpus=corpus, num_topics=num_topics, id2word=dictionary)
#     model.save("../output/lda/lda_mallet/lda_mallet_{num_topics}.model".format(num_topics=num_topics))
#     print "\n \n \nFUKKEN SAVED!!! Не проморгай \n \n \n "

# dictionary = get_dictionary("solo")
# for i, doc in enumerate(raw_tokens.find(fields={"content": 1})):
#     new_vec = dictionary.doc2bow(doc["content"])
#     print i, lda[new_vec]
# texts = [document["content"] for document in raw_tokens.find({},fields={"content": 1})]
# print most_common(texts, 200)

# split into train and test - random sample, but preserving order
grid = collections.defaultdict(list)
train_size = int(round(len(corpus)*0.9))
train_index = sorted(random.sample(xrange(len(corpus)), train_size))
test_index = sorted(set(xrange(len(corpus)))-set(train_index))
train_corpus = [corpus[i] for i in train_index]
test_corpus = [corpus[j] for j in test_index]


for num_topics in range(5, 101, 5):
    model = LDA(dictionary, train_corpus, num_topics, "lda20/lda_training_{num_topics}"
                .format(num_topics=str(num_topics)), passes=20)
    perwordbound = model.log_perplexity(test_corpus)
    perplexity = np.exp2(-perwordbound)

    grid[num_topics].append(perwordbound)
    grid[num_topics].append(perplexity)

df = pd.DataFrame(grid)
ax = plt.figure(figsize=(7, 4), dpi=300).add_subplot(111)
df.iloc[1].transpose().plot(ax=ax,  color="#254F09")

plt.title('Perplexity plot')
plt.ylabel('Perplexity')
plt.xlabel('Topics')
plt.savefig("../output/perplexity100.png")
plt.show()
