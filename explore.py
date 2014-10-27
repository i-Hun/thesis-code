# -*- coding: utf-8 -*-

from pymongo import MongoClient

client = MongoClient()
db = client.thesis
gorod55 = db.gorod55
bk55 = db.bk55
ngs55 = db.ngs55
omskinform = db.omskinform

def count_comments(collection):
    docs_with_comments = 0
    comments_amount = 0

    for doc in collection.find():
        if doc["commentsCount"] != 0:
            docs_with_comments += 1
            comments_amount += doc["commentsCount"]

    print "Количество документов: {docs_count}, из них с комментариями {docs_with_comments}. Всего комментариев {comments_amount}. Среднее количество комментариев {comments_average}."\
        .format(docs_count = collection.count(), docs_with_comments = docs_with_comments, comments_amount = comments_amount, comments_average = comments_amount/collection.count())

count_comments(omskinform)