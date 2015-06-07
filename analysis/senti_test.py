# -*- coding: utf-8 -*-

from __future__ import division

import pymongo
client = pymongo.MongoClient()
db = client.thesis

from senti_strength import RateSentiment

def senti_attr():
    struct = {}
    for i, doc in enumerate(db.docs_topics.find()):
        print i
        if len(doc["comments"]) != 0:
            doc_senti = 0
            for comment in doc["comments"]:
                comment_rating = RateSentiment(comment.encode('utf8'))
                print comment, comment_rating.rate()
                doc_senti += comment_rating.rate()
            for topic, prob in doc["topics"]:
                if topic not in struct:
                    struct[topic] = doc_senti
                else:
                    struct[topic] += doc_senti

    print sorted(struct.items(), key=lambda x: x[1], reverse=True)


def rate_comment_by_expert():
    #204
    import random
    import pickle
    import os.path

    comments = []
    evaluated = []
    path = "/home/hun/Thesis/senti/"

    sample_exist = os.path.isfile(path + "comments_sample")

    if sample_exist:
        sample = pickle.load(open(path + "comments_sample", 'rb'))
    else:
        for i, doc in enumerate(db.docs_topics.find()):
            comments.extend(doc["comments"])
        sample = random.sample(comments, 4000)
        pickle.dump(sample, open(path + "comments_sample", "wb"))

    for i, comment in enumerate(sample[204:]):
        print i, comment + "\n"
        senti = raw_input("Какой эмоциональный заряд несёт данный комментарий? Введите +, - или 0.")

        if senti == "+":
            senti = 1
        elif senti == "-":
            senti = -1
        elif senti == "0":
            senti = 0
        else:
            print("Введите +, - или 0. Вы ввели " + str(senti))
            senti = raw_input("Какой эмоциональный заряд несёт данный комментарий? Введите +, - или 0.")

        # print senti, comment
        evaluated.append((comment, senti))
        pickle.dump(evaluated, open(path + "rated_comments", "wb"))
        print "___________________________________"


# import pickle
# path = "/home/hun/Thesis/senti/"
# sample = pickle.load(open(path + "comments_sample", 'rb'))
# rated = pickle.load(open(path + "rated_comments", 'rb'))
# print rated[-1][0], len(rated), sample[203]

senti_attr()