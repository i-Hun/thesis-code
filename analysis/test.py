# -*- coding: utf-8 -*-
from __future__ import division
from analysis import LDA, get_dictionary, get_corpus
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from settings import config
import os.path
import pickle

db = MongoClient().thesis
raw_tokens = db.raw_tokens
docs_topics = db.docs_topics

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)

def docs_with_this_topic(topic_id):
    """
    Возвращает документы, в которых выбранная тема стоит на первом месте
    """
    counter = 0
    doc_urls = [] # urls документов, в которых эта тема встречается на 1 месте
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    for i, document in enumerate(raw_tokens.find()):

        doc_bow = dictionary.doc2bow(document["content"])
        topics_distr = model[doc_bow]
        topics_distr = sorted(topics_distr, key=lambda x: x[1], reverse=True)
        if topics_distr[0][0] == topic_id:  #номер интересующей нас темы
            counter += 1
            print counter, document["url"], topics_distr[0], document["title"]
            doc_urls.append((document["url"], topics_distr[0]))
    pickle.dump(doc_urls, "docs_with_topic_" + str(topic_id) + ".pickle")

docs_with_this_topic(0)