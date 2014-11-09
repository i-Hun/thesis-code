# -*- coding: utf-8 -*-
from __future__ import division
from pymongo import MongoClient
from sentiments import rate_sentiment

client = MongoClient()
db = client.thesis

def get_collections():
    # names = set(db.collection_names()) - set([u'system.indexes', u'bk55_links', u'ngs55_links', u'omskinform_links'])
    return [collection for collection in db.collection_names() if collection not in [u'system.indexes', u'bk55_links', u'ngs55_links', u'omskinform_links']]

def count_comments(collection):
    docs_with_comments = 0
    comments_amount = 0

    for doc in collection.find():
        if doc["commentsCount"] != 0:
            docs_with_comments += 1
            comments_amount += doc["commentsCount"]

    print "Количество документов: {docs_count}, из них с комментариями {docs_with_comments}. Всего комментариев {comments_amount}. Среднее количество комментариев {comments_average}."\
        .format(docs_count = collection.count(), docs_with_comments = docs_with_comments, comments_amount = comments_amount, comments_average = comments_amount/collection.count())

def rate_comments_in_collection(collection):
    docs = collection.find({}, {"comments": 1})
    print(docs.count())
    for doc in docs:
        print len(doc["comments"])
        if len(doc["comments"]) != 0:
            for comment in doc["comments"]:
                print comment
                print rate_sentiment(comment.encode('utf8'))


for name in get_collections():
    print name
    count_comments(db[name])

# rate_comments_in_collection(db.omskinform)