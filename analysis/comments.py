# -*- coding: utf-8 -*-
from __future__ import division
from pymongo import MongoClient
from senti_strength import rate_sentiment
import datetime
import moment

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
from matplotlib import rc
rc('font', **{'family': 'serif', 'size': 16, 'weight': 'normal'})
rc('text', usetex=True)
rc('text.latex', unicode=True)
rc('text.latex', preamble=r"\usepackage[utf8]{inputenc}")
rc('text.latex', preamble=r"\usepackage[russian]{babel}")

client = MongoClient()
db = client.thesis


def count_comments():
    docs_with_comments = 0
    comments_amount = 0
    plot_list = []

    for doc in db.docs_topics.find():
        if doc["commentsCount"] != 0:
            docs_with_comments += 1
            comments_amount += doc["commentsCount"]

        plot_list.append((doc["date"], doc["commentsCount"]))

    print "Количество документов: {docs_count}, из них с комментариями {docs_with_comments}. Всего комментариев {comments_amount}. Среднее количество комментариев {comments_average}."\
        .format(docs_count=db.docs_topics.count(), docs_with_comments=docs_with_comments, comments_amount=comments_amount, comments_average=comments_amount/db.docs_topics.count())

    plot_list.sort(key=lambda tup: tup[0])
    print plot_list
    x = [i[0] for i in plot_list]
    y = [i[1] for i in plot_list]

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylabel(u'Количество комментариев')
    ax.set_xlabel(u'Дата')
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()
    ax.grid(True)
    plt.savefig('../output/comments.png', bbox_inches='tight', dpi=300)
    plt.show()


def rate_comments(collection):
    docs = collection.find({}, {"comments": 1})
    print(docs.count())
    for doc in docs:
        print len(doc["comments"])
        if len(doc["comments"]) != 0:
            for comment in doc["comments"]:
                print comment
                print rate_sentiment(comment.encode('utf8'))


count_comments()
