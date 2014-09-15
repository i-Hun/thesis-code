# -*- coding: utf-8 -*-

from __future__ import division

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer

import pymorphy2

import re

from bs4 import BeautifulSoup

# импортируем стоп-слова и конвертируем их в utf-8
from nltk.corpus import stopwords
stopwords_ru = [unicode(stopword, 'utf-8') for stopword in stopwords.words('russian')]
additional_stopwords = ["омск", "омске", "омский", "омская", "омское", "омские", "омских", "омска", "м", "мм", "нгс", "ул", "тыс", "который", "это"]
additional_stopwords = [unicode(stopword, 'utf-8') for stopword in additional_stopwords]
stopwords_ru.extend(additional_stopwords)

def tokenize(text):
    # заменяем знаки препинания на пробелы u'.,\\/#!$%^&*;:{}=+_`~()\xab\xbb\u2014\u2026\u2013'
    # TODO: удалить №
    text = re.sub('[.,\/#!$%^&*;:{}=+_`~()«»0-9№]', ' ', text)

    text = text.replace('\\u2026'.decode('unicode-escape'), " ")  # многоточие
    text = text.replace('\\u2014'.decode('unicode-escape'), " ")  # em dash
    text = text.replace('\\u2013'.decode('unicode-escape'), " ")  # en dash
    # дефис оставляю
    #repr()

    text = " ".join(text.split())  # удаляем лишние проблеы

    tokens = [token.lower() for token in text.split()]
    return tokens

def remove_stopwords(tokens):
    filtered_tokens = [w for w in tokens if not w in stopwords_ru]
    return filtered_tokens

def stem(tokens):

    # stemmer = SnowballStemmer("russian")
    # stemmed_tokens = [stemmer.stem(token) for token in tokens]

    morph = pymorphy2.MorphAnalyzer()
    return [morph.parse(token)[0].normal_form for token in tokens]

def preprocess(text):
    return remove_stopwords(stem(tokenize(text)))

def remove_urls(text):
    return re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)

def get_text(html):
    soup = BeautifulSoup(html)
    return soup.get_text(" ", strip=True)
def clear_text(text):
    return " ".join(text.replace("\n", " ").replace("\r", " ").replace("\t", " ").split())