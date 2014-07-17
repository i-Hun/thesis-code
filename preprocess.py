# -*- coding: utf-8 -*-

from __future__ import division

from pymongo import MongoClient

from nltk.stem.snowball import SnowballStemmer

from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer

import pymorphy2

import re

# импортируем стоп-слова и конвертируем их в utf-8
from nltk.corpus import stopwords
stopwords_ru = [unicode(stopword, 'utf-8') for stopword in stopwords.words('russian')]
additional_stopwords = ["омск", "омске", "омский", "омская", "омское", "омские", "омских", "омска", "м", "мм", "нгс", "ул"]
additional_stopwords = [unicode(stopword, 'utf-8') for stopword in additional_stopwords]
stopwords_ru.extend(additional_stopwords)

# подключение к базе данных
client = MongoClient('localhost', 3001)

ngs = client.meteor.ngs

doc = ngs.find_one({"url": "http://ngs55.ru/news/1378625/view/"})

text = doc["content"]

# заменяем знаки препинания на пробелы u'.,\\/#!$%^&*;:{}=+_`~()\xab\xbb\u2014\u2026\u2013'
# TODO: удалить №
text = re.sub('[.,\/#!$%^&*;:{}=+_`~()«»—…–0-9]', ' ', text)

text = text.replace('\\u2026'.decode('unicode-escape'), " ")
text = text.replace('\\u2014'.decode('unicode-escape'), " ")
# text = text.replace('\\u2013'.decode('unicode-escape'), " ")
#repr()

text = " ".join(text.split())  # удаляем лишние проблеы

tokens = [token.lower() for token in text.split()]

# удаляем стоп-слова
filtered_tokens = [w for w in tokens if not w in stopwords_ru]

# for token in filtered_tokens:
#     print token
# приведение к нормальной форме
# stemmer = SnowballStemmer("russian")
# stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]

morph = pymorphy2.MorphAnalyzer()
for token in filtered_tokens:
    print morph.parse(token)[0].normal_form
#
# # for word in stemmed_tokens:
# #     print word
