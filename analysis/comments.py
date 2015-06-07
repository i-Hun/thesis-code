# -*- coding: utf-8 -*-
from __future__ import division
import pymongo
from senti_strength import RateSentiment
import datetime
import moment
import numpy as np
from settings import config
from topics import general_topic_distribution

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
from matplotlib import rc
font = {
    'family': config.get("tex_font_family"),
    'weight': 'normal',
    'size': config.get("tex_font_size")
}
rc('font', **font)

from analysis import LDA, get_dictionary, get_corpus

client = pymongo.MongoClient()
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


def daterange(start_date=datetime.datetime(2013, 8, 30), end_date=datetime.datetime(2014, 9, 01)):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

#################################################################################################

def comments_count_by_day():
    dict = {}
    db.docs_topics.ensure_index([("date", pymongo.ASCENDING)])
    for doc in db.docs_topics.find().sort("date", pymongo.ASCENDING):
        if doc["date"] not in dict.keys():
            dict[doc["date"]] = [1, doc["commentsCount"]]
        else:
            dict[doc["date"]][0] += 1
            dict[doc["date"]][1] += doc["commentsCount"]
    return dict


def comments_count_by_day_complete():

    date_dict = comments_count_by_day()

    weekend_comments = []
    weekday_comments = []

    a = comments_count_by_day().items()
    a = sorted(a, key=lambda x: x[0], reverse=False)
    a = [(date, scores[1]) for date, scores in a]

    fig, ax = plt.subplots()
    ax.plot(*zip(*a))
    for i, single_date in enumerate(daterange()):
        print i
        if single_date.weekday() == 5:
            x_list = [single_date, single_date + datetime.timedelta(1)]
            y_list = [date_dict[single_date][1], date_dict[single_date + datetime.timedelta(1)][1]]
            weekend_comments.extend(y_list)
            print x_list
            ax.fill_between(x_list, y_list, alpha=0.3, color='#FF8E8E')
        elif (single_date.weekday() != 5) and (single_date.weekday() != 6):
            weekday_comments.append(date_dict[single_date][1])
            print single_date.weekday()

    ax.set_ylabel(u'Количество комментариев за день')
    ax.set_xlabel(u'Дата')

    red_patch = mpatches.Patch(color='#FF8E8E', alpha=0.4, label=u"Суббота и воскресенье")
    plt.legend(handles=[red_patch], fontsize=14)

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()  # поворачивает надписи даты
    ax.grid(True)
    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "comments_by_day." + ext,
                format=ext, bbox_inches='tight', dpi=1200)
    plt.show()

    print weekend_comments
    print weekday_comments
    print sum(weekend_comments), len(weekend_comments)
    print sum(weekday_comments), len(weekday_comments)

###################################################


def number_of_docs_by_day():
    date_dict = {date: db.docs_topics.find({"date": date}).count() for date in daterange()}
    print date_dict

    weekend = []
    weekday = []

    fig, ax = plt.subplots()

    for i, single_date in enumerate(daterange()):
        print i
        if single_date.weekday() == 5:
            x_list = [single_date, single_date + datetime.timedelta(1)]
            y_list = [date_dict[single_date], date_dict[single_date + datetime.timedelta(1)]]
            weekend.extend(y_list)
            print x_list
            ax.fill_between(x_list, y_list, alpha=0.3, color='#FF8E8E')
        elif (single_date.weekday() != 5) and (single_date.weekday() != 6):
            weekday.append(date_dict[single_date])
            print single_date.weekday()

    red_patch = mpatches.Patch(color='#FF8E8E', alpha=0.4, label=u"Суббота и воскресенье")
    plt.legend(handles=[red_patch], fontsize=14)

    a = sorted(date_dict.items(), key=lambda x: x[0], reverse=False)
    ax.plot(*zip(*a))
    ax.set_ylabel(u'Количество статей')
    ax.set_xlabel(u'Дата')
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()  # поворачивает надписи даты
    fig.set_figwidth(11)
    ax.grid(True)
    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "docs_by_day." + ext,
                format=ext, bbox_inches='tight', dpi=1200)
    plt.show()
    print sum(weekend), len(weekend), sum(weekend)/len(weekend)
    print sum(weekday), len(weekday), sum(weekday)/len(weekday)

###################################################


def comments_by_topics():
    """
    Здесь документу соответсвует только одна тема, к которой он относится с наибольшей вероятностью
    {"номер темы": [количество документов, количество комментов]}
    """
    struct = {}
    for doc in db.docs_topics.find():
        top_topic = sorted(doc["topics"], key=lambda x: x[1], reverse=True)[0][0]
        if top_topic not in struct.keys():
            struct[top_topic] = [1, doc["commentsCount"]]
        else:
            struct[top_topic][1] += doc["commentsCount"]
            struct[top_topic][0] += 1

    return struct


def most_commented_topics1():
    a = []
    for topic, j in comments_by_topics().items():
        a.append((topic, j[1]/j[0]))

    print sorted(a, key=lambda x: x[1], reverse=True)


def most_commented_topics2():
    """
    Выводит список тем с индексом комментируемости, рассчитанным как произведение количество комментов к документу,
     на вероятность отнесения документа к теме.

     Эти значения не очень полезны, посколько на них влияет распространённость темы, а нам нужна комментируемость.
    """
    struct = {}
    for doc in db.docs_topics.find():
        for topic, prob in doc["topics"]:
            if topic not in struct:
                struct[topic] = prob * doc["commentsCount"]
            else:
                struct[topic] += prob * doc["commentsCount"]

    print sorted(struct.items(), key=lambda x: x[1], reverse=True)

def most_commented_topics3():
    """
    Как most_commented_topics2, только умножаем на распространённость темы
    """
    struct = {}
    result = {}
    topics_distr = general_topic_distribution()

    for doc in db.docs_topics.find():
        for topic, prob in doc["topics"]:
            if topic not in struct:
                struct[topic] = prob * doc["commentsCount"]
            else:
                struct[topic] += prob * doc["commentsCount"]

    struct = struct.items()

    for i in struct:
        print i, topics_distr[i[0]]
        result[i[0]] = i[1] / topics_distr[i[0]]

    return sorted(result.items(), key=lambda x: x[1], reverse=True)

print most_commented_topics3()