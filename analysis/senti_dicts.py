# -*- coding: utf-8 -*-

import pymorphy2
import codecs
from settings import config

def get_all_forms(word):
    """Полный разбор слова"""
    morph = pymorphy2.MorphAnalyzer()
    for i in morph.parse(word):
        for j in i.lexeme:
            print j.word

def test_short_rules():
    """Получаем список всех слов из трёх букв с оператором *"""
    dict = "{0}/Thesis/senti/dict/ru/EmotionLookupTable.txt".format(config.get("home_path"))
    morph = pymorphy2.MorphAnalyzer()
    with open(dict) as f:
        for num, line in enumerate(f):
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0].strip().decode("utf8")
            # print num, word, len(word.decode("utf8"))
            if len(word) < 5 and word.endswith("*"):
                print word
            # print "_____________________"

# test_short_rules()
get_all_forms(u'ад')

def tuple_from_dict():
    path1 = "{0}/Thesis/senti/dict/ru/EmotionLookupTable.txt".format(config.get("home_path"))
    path2 = "{0}/Thesis/senti/dict/ru2/EmotionLookupTable.txt".format(config.get("home_path"))
    path3 = "{0}/Thesis/senti/dict/ru3/EmotionLookupTable.txt".format(config.get("home_path"))

    dict1 = []
    dict2 = []
    dict3 = []

    with open(path1) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict1.append((word, score))

    with open(path2) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict2.append((word, score))

    with open(path3) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict3.append((word, score))

    return dict1 + dict2 + dict3


# java -jar /Users/olegnagornyy/Thesis/senti/SentiStrengthCom.jar sentidata /Users/olegnagornyy/Thesis/senti/dict/ru/ stdin noDictionary illegalDoubleLettersInWordMiddle ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded explain text сука+блять
