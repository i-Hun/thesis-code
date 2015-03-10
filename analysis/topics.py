# -*- coding: utf-8 -*-
from __future__ import division
from analysis import LDA, get_dictionary, get_corpus
from pymongo import MongoClient
from bson.objectid import ObjectId
import random


db = MongoClient().thesis
raw_tokens = db.raw_tokens
docs_topics = db.docs_topics

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)

# doc_ids = random.sample(range(1, 1000), 50)
# filtered = filter(lambda enum_bow: enum_bow[0] in doc_ids, enumerate(corpus[:1000]))
# subset = [bow for enum, bow in filtered]  # убрать ограничения



def topic_distribution_subset(subset):
    """
    Суммируем вектора. Насчёт деления на количество векторов не уверен
    """
    from collections import OrderedDict
    topic_distribution_dict = {}
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    for doc_bow in subset:
        topic_distribution = model[doc_bow]
        for topic_id, score in topic_distribution:
            if topic_id not in topic_distribution_dict.keys():
                topic_distribution_dict[topic_id] = score

            else:
                topic_distribution_dict[topic_id] += score
    for i in topic_distribution_dict.iteritems():
        topic_distribution_dict[i[0]] = i[1]/len(subset)

    return sorted(topic_distribution_dict.items(), key=lambda x: x[1], reverse=True)


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


def sinle_topic():
    """
    Определим одну самую вероятную тема для каждого документа. Возратим массив этих тем.
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
    dict_vector = {}

    for num, doc in enumerate(corpus):
        print num
        for word_id, count in doc:
            if word_id not in dict_vector:
                dict_vector[word_id] = count
            else:
                dict_vector[word_id] += count
    print len(dict_vector), dict_vector

    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    print sorted(model[create_single_vector()], key=lambda x: x[1], reverse=True)

    return dict_vector.items()


def create_single_vector2():
    texts = (document["content"] for document in raw_tokens.find(fields={"content": 1}))
    # texts = sum(texts, [])
    new_list = []
    for i in texts:
        new_list.extend(i)

    print len(new_list)
    corp = dictionary.doc2bow(new_list)
    model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
    topics_distribution = model[corp]
    print sorted(topics_distribution, key=lambda x: x[1], reverse=True)

model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
for i, document in enumerate(raw_tokens.find()):

    doc_bow = dictionary.doc2bow(document["content"])
    topics_distr = model[doc_bow]
    topics_distr = sorted(topics_distr, key=lambda x: x[1], reverse=True)
    if topics_distr[0][0] == 2:  #номер интересующей нас темы
        print document["url"], topics_distr[0], topics_distr[1], document["title"]