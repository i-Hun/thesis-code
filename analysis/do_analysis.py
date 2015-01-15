# -*- coding: utf-8 -*-
from analysis import LDA, get_dictionary, get_corpus
from gensim import corpora, models

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)

# Обычный LDA
# lda = LDA(dictionary, corpus, 20, "20topics")
# for i, topic in enumerate(lda.show_topics(num_topics=lda.num_topics, num_words=20)):
#     print i+1, topic

#hLDA
# hlda = hLDA(dictionary, corpus)
# for i, topic in enumerate(hlda.show_topics(topics=-1)):
#     print i+1, topic


# MALLET LDA
model = models.LdaMallet('../mallet-2.0.7/bin/mallet', corpus=corpus, num_topics=20, id2word=dictionary)
model.show_topics(num_topics=-1, num_words=10, log=False, formatted=True)
# model.save("/home/hun/thesis-python/tmp/lda_mallet_20.model")
# corpus_lda = lda[corpus]
# print corpus_lda

# dictionary = get_dictionary("solo")
# for i, doc in enumerate(raw_tokens.find(fields={"content": 1})):
#     new_vec = dictionary.doc2bow(doc["content"])
#     print i, lda[new_vec]
# texts = [document["content"] for document in raw_tokens.find({},fields={"content": 1})]
# print most_common(texts, 200)

