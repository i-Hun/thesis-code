# -*- coding: utf-8 -*-
from __future__ import division
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora, models, similarities, matutils
import numpy as np
import scipy.stats as stats
from scipy.sparse import linalg as splinalg
from scipy.sparse import *
import matplotlib.pyplot as plt
# import h5py

from pymongo import MongoClient
db = MongoClient().thesis
raw_tokens = db.raw_tokens

from analysis import LDA, get_corpus, get_dictionary

# Define KL function
def sym_kl(p, q):
    return np.sum([stats.entropy(p, q), stats.entropy(q, p)])


dictionary = get_dictionary("solo")

class MyCorpus(object):
    def __iter__(self):
        for doc in raw_tokens.find(fields={"content": 1}):
            yield dictionary.doc2bow(doc["content"])

my_corpus = MyCorpus()

l = np.array([sum(cnt for _, cnt in doc) for doc in my_corpus])
def arun(corpus, dictionary, min_topics=20, max_topics=50, step=10):
    print "Arun runing"
    kl = []
    for i in range(min_topics, max_topics, step):
        lda = LDA(dictionary, corpus, i, str(i) + "topics")
        m1 = lda.expElogbeta
        U, cm1, V = np.linalg.svd(m1)
        #Document-topic matrix
        lda_topics = lda[my_corpus]
        m2 = matutils.corpus2dense(lda_topics, lda.num_topics).transpose()
        cm2 = l.dot(m2)
        cm2 = cm2 + 0.0001
        print "cm2norm begin"
        cm2norm = np.linalg.norm(l)
        print "cm2norm end"
        cm2 = cm2/cm2norm
        # cm2 = csr_matrix(cm2).todense()
        print len(cm1)
        kl.append(sym_kl(cm1, cm2))
    return kl

kl = arun(my_corpus, dictionary, min_topics=20, max_topics=50)

# Plot kl divergence against number of topics
plt.plot(kl)
plt.ylabel('Symmetric KL Divergence')
plt.xlabel('Number of Topics')
plt.savefig('kldiv.png', bbox_inches='tight')