# -*- coding: utf-8 -*-

from pymongo import MongoClient
import re

from preprocess import preprocess
from analysis import most_common

client = MongoClient()
db = client.thesis
omskinform = db.omskinform

def tokenize_texts(collection):
    tokenized_docs = []

    for doc in db[collection].find()[:1000]:
        print doc["url"]
        text = doc["title"] + " " + doc["content"]
        tokenized_doc = preprocess(text)
        tokenized_docs.append(tokenized_doc)
        print len(tokenized_docs)

    return tokenized_docs


# most_common(tokenize_texts("omskinform"), 100)