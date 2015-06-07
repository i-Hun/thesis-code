# -*- coding: utf-8 -*-

from pymongo import MongoClient
from preprocess import tokenize_pattern, remove_punct, stem_pymorphy, remove_stopwords, preprocess
from analysis import most_common
from pattern.en import tokenize

client = MongoClient()
db = client.thesis
gorod55 = db.gorod55

def rc1(text):
    head, sep, tail = text.rpartition(u'По материалам')
    if head:
        if len(tail) > 300:
            print u"\n" + sep + tail + u"\n"
        return head
    else:
        return text

def rc2(text):
    head, sep, tail = text.rpartition(u'Фото:')
    if head:
        if len(tail) > 300:
            print u"\n" + sep + tail + u"\n"
        return head
    else:
        return text

def rc3(text):
    head, sep, tail = text.rpartition(u'Верхнее фото:')
    if head:
        if len(tail) > 300:
            print u"\n" + sep + tail + u"\n"
        return head
    else:
        return text

def rc4(text):
    head, sep, tail = text.rpartition(u'Фото в тексте:')
    if head:
        if len(tail) > 300:
            print u"\n" + sep + tail + u"\n"
        return head
    else:
        return text

def remove_foto_container(text):
    """В некоторых документах спарсилось вместе с CSS в конце. Удалить"""
    head, sep, tail = text.rpartition(u'#foto_container')
    if head:
        print "head: {0}, sep: {1}, tail: {2}".decode("utf-8").format(head, sep, tail)
        return head
    else:
        return text

def remove_copyright(text):
    """
    for doc in gorod55.find({"content": {'$regex': 'По материалам'}}):
    gorod55.update({'_id': doc['_id']}, {'$set':{'content': remove_copyright(doc["content"])}})
    """
    return rc4(rc3(rc2(rc1(text))))


def tokenize_texts(collection):
    tokenized_docs = []

    for doc in db[collection].find()[:1000]:
        print doc["url"]
        text = doc["title"] + " " + doc["content"]
        tokenized_doc = preprocess(text)
        tokenized_docs.append(tokenized_doc)
        print len(tokenized_docs)

    return tokenized_docs


most_common(tokenize_texts("gorod55"), 100)
