# -*- coding: utf-8 -*-
from __future__ import division
from pymongo import MongoClient
from preprocess import preprocess
from analysis import remove_alone
import itertools

db = MongoClient().thesis
omskinform_tokens = db.omskinform_tokens


def tokenize_texts(collection):
    """
    Принимает имя коллекции.
    Возвращает список документов вида [[токен1, токен2], [токен1, токен3]]
    """
    tokenized_docs = []

    for doc in db[collection].find():
        print doc["url"]
        text = doc["title"] + " " + doc["content"]
        tokenized_doc = preprocess(text)
        tokenized_docs.append(tokenized_doc)
        print(str(len(tokenized_docs)) + "\n")

    return tokenized_docs

# for doc in db.omskinform.find():
#     content = preprocess(doc["title"] + " " + doc["content"])
#     doc["content"] = content
#     omskinform_tokens.insert(doc)


# documents = [document["content"] for document in omskinform_tokens.find(fields={"content": 1})]
#
# def remove_alone1(documents):
#     """ На входе принимаем токенизированный список документов
#     вида [[токен1, токен2], [токен1, токен3]]"""
#
#     from collections import Counter
#
#     c = Counter(token for document in documents for token in document)
#
#     docs = []
#     single = []
#
#     for document in documents:
#         doc = []
#         for token in document:
#             if c[token] < 2:
#                 print "Одиночный токен: {0}".decode("utf8").format(token)
#                 single.append(token)
#             else:
#                 doc.append(token)
#         docs.append(doc)
#
#     print "Найдёно {0} уникальных токенов".format(single_count)
#     return docs
#
# remove_alone1(documents)