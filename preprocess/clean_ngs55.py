# -*- coding: utf-8 -*-

from pymongo import MongoClient
from analysis import most_common
from preprocess import tokenize_pattern, remove_punct, stem_pymorphy, remove_stopwords, preprocess
import re

client = MongoClient()
db = client.thesis
ngs55 = db.ngs55

def tokenize_texts(collection):
    tokenized_docs = []

    for doc in db[collection].find()[:1000]:
        print doc["url"]
        text = doc["title"] + " " + doc["content"]
        tokenized_doc = preprocess(text)
        tokenized_docs.append(tokenized_doc)
        print len(tokenized_docs)

    return tokenized_docs


def rm_parts_and_below():
    for doc in ngs55.find({"content": {"$regex": re.compile("НГС\.НОВОСТИ")}}):

        text = doc["content"]
        output = None
        for word in ["НГС.НОВОСТИ"]:
            head, sep, tail = text.rpartition(word.decode('utf-8'))
            if head:
                if (not output) or (output and len(output) > len(head)):
                    if len(tail) < 250:
                        output = head
                        print "rm_parts_and_below: {0}".format((sep + tail).encode("UTF-8"))
                    else:
                        print "URL " + doc["url"]
                        print "rm_parts_and_below: {0}".format((head + sep + tail).encode("UTF-8"))
                        if not output:
                            output = text
            else:
                if not output:  # если после проверок всех авторов ничего не изменено, возвращаем исходный текст
                    output = text

        ngs55.update({"_id": doc["_id"]}, {"$set": {"content": output}})

def rm_parts():
    for doc in ngs55.find({"content": {"$regex": re.compile("НГС\.НОВОСТИ")}}):
        new_text = re.sub(u"НГС\.НОВОСТИ", "", doc["content"])
        ngs55.update({"_id": doc["_id"]}, {"$set": {"content": new_text}})

# rm_parts_and_below()
# rm_parts()
# most_common(tokenize_texts("gorod55"), 100)
# print ngs55.find({"content": {"$regex": re.compile("Фото:")}}).count()

"""
нгс.новость: 1260
фото: 1022
пресс-служба: 426
thinkstockphotos.com: 348
нгс: 275

Статья http://ngs55.ru/news/1807051/view/ и http://ngs55.ru/news/1826271/view/ криво спарсилась. Удалить
"""