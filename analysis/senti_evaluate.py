# -*- coding: utf-8 -*-

from settings import config
from lxml import etree
from senti_strength import RateSentiment
import pickle

def eval_romip():
    """
    Чмтаем news_eval_final.xml.
    Записываем результат обработки тестовой коллекции в виде
    [(балл экспертов, балл SentiStrength), () ...]
    """
    path = "{0}/Thesis/senti/training/news_eval_final.xml".format(config.get("home_path"))

    file = open(path, "r")
    xml = etree.parse(file)
    file.close()

    num = 0
    eval_results = []

    for sentence in xml.xpath('//sentence'):
        text = sentence.getchildren()[0].text.strip()
        rating = sentence.getchildren()[1].text.strip()
        if rating is "0" or rating is "+" or rating is "-":
            num += 1
            ss = RateSentiment(text.encode('utf8'), "default/ru").rate()  # изменить путь для другого словаря
            eval_results.append((rating, ss))
            print num
        # изменить путь для другого словаря
        pickle.dump(eval_results, open("{0}/Thesis/senti/training/ru_dicts".format(config.get("home_path")), "w"))

def matches(path):
    """
    Подсчитываем количество совпадений между тестовой коллекцией и работой SentiStrength
    """
    count = 0
    path = "{0}/Thesis/senti/training/{1}".format(config.get("home_path"), path)

    fileObject = open(path, 'r')
    data = pickle.load(fileObject)
    fileObject.close()

    for tup in data:
        rating = tup[0]
        ss = tup[1]

        if ss < 0 and rating == "-":
            count += 1
        if ss > 0 and rating == "+":
            count += 1
        if ss == 0 and rating == "0":
            count += 1

    print "Совпадений: {0}".format(count)


"""
for i in ["final_dicts", "ru_dicts", "ru2_dicts"]:
    matches(i)
Совпадений: 1931 50%
Совпадений: 1835 47%
Совпадений: 1208
"""

def rate_comment_by_expert():

    import random
    import pickle
    import os.path

    comments = []
    evaluated = []
    path = "{0}/Thesis/senti/".format(config.get("home_path"))

    sample_exist = os.path.isfile(path + "comments_sample_test")

    if sample_exist:
        sample = pickle.load(open(path + "comments_sample_test", 'rb'))
    else:
        for i, doc in enumerate(db.docs_topics.find()):
            comments.extend(doc["comments"])
        sample = random.sample(comments, 300)
        pickle.dump(sample, open(path + "comments_sample_test", "wb"))

    for i, comment in enumerate(sample):
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

        evaluated.append((comment, senti))
        pickle.dump(evaluated, open(path + "rated_comments_test", "wb"))
        print "___________________________________"