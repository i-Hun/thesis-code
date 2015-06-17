# -*- coding: utf-8 -*-

from __future__ import division
from settings import config
from preprocess import preprocess

import pymongo
from bson import ObjectId
client = pymongo.MongoClient()
db = client.thesis
final_db = db.final_db
docs_topics = db.docs_topics

from senti_strength import RateSentiment

def senti_db_update():
    # Если проводить поиск и изменение на одной коллекции
    # FIXME через некоторое время работы, появляется ошибка AttributeError: 'list' object has no attribute 'encode'
    # Вероятно, причина в том, что на изменение подаются уже изменённые данные
    for i, doc in enumerate(docs_topics.find().batch_size(25)):
        print i, doc["url"], len(doc["comments"])
        if not final_db.find_one({"url": doc["url"]}):
            comments_senti = []
            if len(doc["comments"]) != 0:
                for comment in doc["comments"]:
                    if comment:
                        comment = preprocess.clear_text(comment)
                        comment_rating = RateSentiment(comment.encode('utf8'), "final").rate()
                        comments_senti.append((comment, comment_rating))
                doc["comments"] = comments_senti
            final_db.insert_one(doc)


def senti_by_topics():
    """
    Подсчитываем среднюю тональность для каждой темы
    {"номер темы": "средний тональный балл"}
    """
    from topics import general_topic_distribution
    import pickle

    struct = {}
    result = {}
    topics_distr = general_topic_distribution()

    for doc in db.final_db.find():
        if len(doc["comments"]):
            doc_rating = 0
            for comment, rating in doc["comments"]:
                doc_rating += rating
            avg_doc_rating = doc_rating / len(doc["comments"])

            for topic_id, prob in doc["topics"]:
                if topic_id not in struct.keys():
                    struct[topic_id] = avg_doc_rating * prob
                else:
                    struct[topic_id] += avg_doc_rating * prob

    for i in struct.items():
        result[i[0]] = i[1] / topics_distr[i[0]]

    result = sorted(result.items(), key=lambda x: x[1], reverse=True)

    most_positiv_value = result[0][1]

    for num, i in enumerate(result):
        print "{num} & {topic_id}. {topic_name} & {percent}\\% \\\\".format(num=num+1,
                                                                            topic_id=i[0],
                                                                            topic_name=config.topics_by_id(i[0]),
                                                                            percent=round(i[1]/most_positiv_value * 100, 1))

    return result


def senti_by_topics_single():
    """
    Здесь документу соответсвует только одна тема, к которой он относится с наибольшей вероятностью
    {"номер темы": [количество документов, количество комментов]}
    Для этой темы определяем среднюю оценку тональности
    Представление данных:
    sorted_data = sorted(senti_by_topics_single().items(), key=lambda item: item[1][1]/item[1][0], reverse=True)
    for item in sorted_data:
    print item[0], item[1][1]/item[1][0]
    """
    struct = {}
    for doc in db.final_db.find():
        if len(doc["comments"]):
            doc_rating = 0
            for comment, rating in doc["comments"]:
                doc_rating += rating
            avg_doc_rating = doc_rating / len(doc["comments"])

            top_topic = sorted(doc["topics"], key=lambda x: x[1], reverse=True)[0][0]
            if top_topic not in struct.keys():
                struct[top_topic] = [1, avg_doc_rating]
            else:
                struct[top_topic][0] += 1  # количество докуметов с этой главной темой
                struct[top_topic][1] += avg_doc_rating  # накопленный средний рейтинг
    return struct
