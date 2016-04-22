# -*- coding: utf-8 -*-
from __future__ import division
from analysis import LDA, get_dictionary, get_corpus
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from settings import config
import os.path
import pickle

db = MongoClient().thesis
raw_tokens = db.raw_tokens
docs_topics = db.docs_topics

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)


def general_topic_distribution(collection="docs_topics", **params):  # collection="", selector={}
    """
    Суммируем вектора. Насчёт деления на количество векторов не уверен. Лучший способ подсчёта популярности тем
    """
    selector = params.get("selector", {})
    print collection, selector

    path = "{0}/Thesis/code/output/general_topic_distribution".format(config.get("home_path"))
    data_exists = os.path.isfile(path)

    topic_distribution_dict = {}
    for doc in db[collection].find(selector):
        topic_distribution = doc["topics"]
        for topic_id, score in topic_distribution:
            if topic_id not in topic_distribution_dict.keys():
                topic_distribution_dict[topic_id] = score
            else:
                topic_distribution_dict[topic_id] += score
    for i in topic_distribution_dict.iteritems():
        topic_distribution_dict[i[0]] = i[1]/db[collection].find(selector).count()

    # result_tuples = sorted(topic_distribution_dict.items(), key=lambda x: x[1], reverse=True)
    # for num, i in enumerate(result_tuples):
    #     print "{num} & {topic_id}. {topic_name} & {prob} \\\\".format(num=num+1,
    #                                                                         topic_id=i[0],
    #                                                                         topic_name=config.topics_by_id(i[0]),
    #                                                                         prob=round(i[1], 4))
    print "topic_distribution: ", topic_distribution_dict
    return topic_distribution_dict


def average_topics(threshold=0.01):
    """
    Подсчитаем, ко скольким темам можно отнести документы при заданом пороге. Найдём среднее количество тем для каждого документа.
    """
    from collections import Counter

    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    topics_number = []

    topics_distribution = model[corpus]
    for topic_distribution in topics_distribution:
        topic_distribution = [(topic_id, probability) for topic_id, probability in topic_distribution if probability >= threshold]
        print topic_distribution
        topics_number.append(len(topic_distribution))

    count_topics = Counter(topics_number)
    result = sum(topics_number)/len(topics_distribution)
    print "Среднее количество тем в {0} документах: {1}".format(len(topics_distribution), result)
    print count_topics
    return result


def single_topic():
    """
    Определим одну самую вероятную тема для каждого документа. Результат --
    список тем с указанием количества документов, которые могут быть отнесены к ней с наибольшей вероятностью
    """
    from collections import Counter

    topics = []

    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    topics_distribution = model[corpus]
    for topic_distribution in topics_distribution:
        a = sorted(topic_distribution, key=lambda x: x[1])
        print a[-1]
        topics.append(a[-1][0])
    c = Counter(topics)
    print c


def create_single_vector():
    """
    Возвращает единый вектор. По факту это то же самое, что сложить тексты и создать из них вектор.
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    print sorted(model[create_single_vector()], key=lambda x: x[1], reverse=True)
    """
    path = "{0}/Thesis/code/output/topics/single_vector".format(config.get("home_path"))
    data_exists = os.path.isfile(path)

    if data_exists:
        fileObject = open(path, 'rb')
        dict_vector = pickle.load(fileObject)
        return dict_vector.items()
    else:
        dict_vector = {}

        for num, doc in enumerate(corpus):
            for word_id, count in doc:
                if word_id not in dict_vector:
                    dict_vector[word_id] = count
                else:
                    dict_vector[word_id] += count

        pickle.dump(dict_vector, open(path, "wb"))
        return dict_vector.items()


def create_single_vector_text():
    """
    Результат такой же, что и в первом варианте функции. Но достигается за счёт складывания непосредственно текстов
    """
    texts = (document["content"] for document in raw_tokens.find(projection={"content": 1}))
    # texts = sum(texts, [])
    new_list = []
    for i in texts:
        new_list.extend(i)

    print len(new_list)
    corp = dictionary.doc2bow(new_list)
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    topics_distribution = model[corp]
    print sorted(topics_distribution, key=lambda x: x[1], reverse=True)


def docs_with_this_topic(topic_id):
    """
    Возвращает документы, в которых выбранная тема стоит на первом месте
    """
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    model.minimum_probability = 0.1
    for i, document in enumerate(raw_tokens.find()):

        doc_bow = dictionary.doc2bow(document["content"])
        topics_distr = model[doc_bow]
        topics_distr = sorted(topics_distr, key=lambda x: x[1], reverse=True)
        if topics_distr[0][0] == topic_id:  #номер интересующей нас темы
            print document["url"], topics_distr[0], document["title"]


def single_vector_distribution():
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    print sorted(model[create_single_vector()], key=lambda x: x[1], reverse=True)

#_________________________________________

def topics_by_sources():
    """ Показывает в каких СМИ какие темы наиболее распространены
        Возвращает {"источник": {topic_id: prob, topic_id: prob, ...}}
    """
    sources = ["bk55_preprocessed", "gorod55", "ngs55", "omskinform"]
    result = {}
    for source in sources:
        selector = {"source": source}
        # print source.upper()
        result[source] = general_topic_distribution(selector=selector)
    return result


def get_topics_positions(topics_by_sources):
    """
    На входе список тем по источнику из функции topics_by_sources() :
    {"источник": {topic_id: prob, topic_id: prob, ...}}
    Возвращает словарь вида {"источник": [("позиция": "тема"), ()], "источник": [(), ()]}
    """
    result = {}
    for source, data in topics_by_sources.items():
        sorted_list = sorted(data.items(), key=lambda x: x[1], reverse=True)  # (номер темы, вероятность)
        rating_list = []  # (место, номер темы)
        for num, tuple in enumerate(sorted_list):
            rating_list.append((num + 1, tuple[0]))
        result[source] = rating_list
    # print "get_topics_positions: ", result
    return result


def get_topics_positions_format(topics_positions):
    """
    Принимает результаты фнкции get_topics_positions и форматирует их
    """
    result = {}
    for source, data in topics_positions.items():
        for position, topic in data:
            result.setdefault(topic, {}).update({source:position})
    print "get_topics_positions_format: ", result  # result = {0: {'bk55_preprocessed': 17, 'ngs55': 6, 'gorod55': 35, 'omskinform': 14}, 1: {'bk55_preprocessed': 1,
    for i in result.items():
        print "{topic_id}. {topic_name} & {bk55} & {ngs55} & {gorod55} & {omskinform} \\\\".format(topic_id=i[0], topic_name=config.topics_by_id(i[0]),
                                                              bk55=i[1]["bk55_preprocessed"],
                                                              ngs55=i[1]["ngs55"],
                                                              gorod55=i[1]["gorod55"],
                                                              omskinform=i[1]["omskinform"])


def most_different_sources():
    import itertools
    import math

    sources = ["bk55_preprocessed", "gorod55", "ngs55", "omskinform"]

    for pair in itertools.combinations(sources, 2):
        first = {}
        second = {}

        print pair
        selector1 = {"source": pair[0]}
        selector2 = {"source": pair[1]}
        for topic, prob in general_topic_distribution(selector=selector1).items():
            first[topic] = prob
        for topic, prob in general_topic_distribution(selector=selector2).items():
            second[topic] = prob

        sums = 0
        for topic, prob in first.items():
            sum = math.fabs(second[topic] - prob)
            sums +=sum
        print "sums", sums


docs_with_this_topic(39)
