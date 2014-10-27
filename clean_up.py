# -*- coding: utf-8 -*-

from pymongo import MongoClient
from preprocess import tokenize_pattern, remove_punct, stem_pymorphy, remove_stopwords
from analysis import most_common


client = MongoClient()
db = client.thesis
gorod55 = db.gorod55

def rc1(text):
    head, sep, tail = text.rpartition(u'По материалам')
    if head:
        print u"\n Удален копирайт: " + sep + tail + u"\n"
        return head
    else:
        return text

def rc2(text):
    head, sep, tail = text.rpartition(u'Фото:')
    if head:
        print u"\n Удален копирайт: " + sep + tail + u"\n"
        return head
    else:
        return text

def rc3(text):
    head, sep, tail = text.rpartition(u'Верхнее фото:')
    if head:
        print u"\n Удален копирайт: " + sep + tail + u"\n"
        return head
    else:
        return text

def rc4(text):
    head, sep, tail = text.rpartition(u'Фото в тексте:')
    if head:
        print u"\n Удален копирайт: " + sep + tail + u"\n"
        return head
    else:
        return text

def remove_copyright(text):
    return rc4(rc3(rc2(rc1(text))))

texts_arr = [doc["title"] + " " + remove_copyright(doc["content"]) for doc in gorod55.find()]

tokens_arr = [remove_stopwords(remove_punct(tokenize_pattern(text))) for text in texts_arr]

most_common(tokens_arr, 100)

for separ in separs:
    head, sep, tail = text.rpartition(separ)