# -*- coding: utf-8 -*-
import logging

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
log = logging.getLogger("merge")

from datetime import datetime

from pymongo import MongoClient
from preprocess import preprocess, remove_stopwords, replace_tokens

client = MongoClient()
db = client.thesis
merged = db.merged
raw_tokens = db.raw_tokens


def merge_collections():
    collections = ["bk55_preprocessed", "gorod55", "ngs55", "omskinform"]
    for collection in collections:
        print db[collection].find().count()
        for doc in db[collection].find():
            doc["source"] = collection
            del doc["_id"]
            merged.insert(doc)


def make_tokens():
    #FIXME
    """ если просто обновлять базу на новые значения
    # general.update({"_id": doc["_id"]}, {"$set": {"content": tokens}})
    # то почему-то на некоторых документах функция препроцессинга применятеся дважды
    # и возникает ошибка складывания строки с массивом (doc["title"] + " " + doc["content"])"""
    count = 1
    for doc in merged.find():
        print count
        try:
            tokens = preprocess(doc["title"] + " " + doc["content"])
            doc["content"] = tokens
            del doc["_id"]
            raw_tokens.insert(doc)
        except Exception as e:
            log.error("{0}: {1}".format(count, e))
            log.error("Source: {0}. Title: {1}. Content {2}. URL: {3}".decode("utf8").format(doc["source"], doc["title"], doc["content"], doc["url"]))
        count += 1


def validate_doc(doc):
    # Валидация URL не требуется. Не валидный не получилось бы спарсить

    if not isinstance(doc["title"], basestring):
        raise ValueError("title must be string. URL: " + doc["url"])

    if not isinstance(doc["date"], datetime):
        raise ValueError("date must be datetime. URL: " + doc["url"])

    #  Проблемы были на http://ngs55.ru/news/1910311/view/ и http://www.bk55.ru/mc2/news/article/1939
    if len(doc["comments"]) != doc["commentsCount"]:
        raise ValueError("comments length must be the same as commentsCount. URL: " + doc["url"])

    if not isinstance(doc["commentsCount"], int):
        raise ValueError("commentsCount must be number. URL: " + doc["url"])

# merge_collections()
# make_tokens()
#
# raw_tokens.update({"url": "http://www.bk55.ru/mc2/news/article/1939"}, {"$set": {"commentsCount": 0}})
# raw_tokens.update({"url": "http://ngs55.ru/news/1910311/view/"}, {"$set": {"commentsCount": 19}})
#
# for doc in raw_tokens.find():
#     validate_doc(doc)
#     print "Проверка завершена"
