# -*- coding: utf-8 -*-
from __future__ import division
# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora, models, similarities, matutils
import numpy as np
import scipy.stats as stats
import pickle
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import rc
rc('font', **{'family': 'serif', 'size': 16, 'weight': 'normal'})
rc('text', usetex=True)
rc('text.latex', unicode=True)
rc('text.latex', preamble=r"\usepackage[utf8]{inputenc}")
rc('text.latex', preamble=r"\usepackage[russian]{babel}")
# import h5py
import scipy.sparse
from sparsesvd import sparsesvd

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
def arun(corpus, dictionary, min_topics=10, max_topics=21, step=5):
    print "Arun runing"
    output = []
    for i in range(min_topics, max_topics, step):
        lda = LDA(dictionary, corpus, i, "lda20/lda_training_" + str(i))
        print "Модель построена/загружена"
        m1 = lda.expElogbeta
        # U, cm1, V = np.linalg.svd(m1)
        smat = scipy.sparse.csc_matrix(m1)  # convert to sparse CSC format
        U, cm1, V = sparsesvd(smat, i + 30)  # do SVD, asking for 100 factors
        print "sparsesvd сделано"
        #Document-topic matrix
        lda_topics = lda[my_corpus]
        m2 = matutils.corpus2dense(lda_topics, lda.num_topics).transpose()
        cm2 = l.dot(m2)
        cm2 = cm2 + 0.0001
        print "cm2norm begin"
        cm2norm = np.linalg.norm(l)
        print "cm2norm end"
        cm2 = cm2/cm2norm
        print len(cm1), len(cm2)
        kl = sym_kl(cm1, cm2)
        output.append((i, kl))
        print i, kl
    print output
    return output

# output = arun(my_corpus, dictionary, min_topics=5, max_topics=101)

fileObject = open("../output/kl",'r')
output = pickle.load(fileObject)

num = [i[0] for i in output]
kl = [i[1] for i in output]
# Plot kl divergence against number of topics
plt.plot(num, kl)
plt.ylabel(u'Расстояние Кульбака — Лейблера')
plt.xlabel(u'Количество тем')
plt.savefig('../output/kldiv.png', bbox_inches='tight')
plt.show()
