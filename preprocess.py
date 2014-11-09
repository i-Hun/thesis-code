# -*- coding: utf-8 -*-

from __future__ import division

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer

import pymorphy2

from pattern.en import tokenize

import re

# импортируем стоп-слова и конвертируем их в utf-8
from nltk.corpus import stopwords
stopwords_ru = stopwords.words('russian')
additional_stopwords = []
additional_stopwords = [unicode(stopword, 'utf-8') for stopword in additional_stopwords]
stopwords_ru.extend(additional_stopwords)

def tokenize_regexp(text):
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
    print "Tokenize with regexp"
    return tokens

def tokenize_pattern(text):
    """
    The tokenize() function returns a list of sentences, with punctuation marks split from words.
    """
    sents = tokenize(text, punctuation=".,;:!?()[]{}`''\"@#$^&*+-|=~_«»…".decode("utf8"), replace={})
    """
    Возвращает список предложений вида
    Теперь , в 2014 году , голая Дженнифер Лоуренс появилась в Интернете за полтора месяца до всемирной премьеры первой части последней серии трилогии « Голодные игры : Сойка-пересмешница » ( The Hunger Games : Mockingjay – Part 1 ) .
    """
    tokens = [token.lower() for sent in sents for token in sent.split()]
    print "Tokenize with Pattern"
    return tokens

def remove_urls(text):
    without_urls =  re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
    print "URLs removed"
    return without_urls

def remove_stopwords(tokens):
    filtered_tokens = [w for w in tokens if not w in stopwords_ru]
    print "Stopwords removed"
    return filtered_tokens

def remove_punct(tokens):
    """
    Если убрать .decode("utf8")] (перегодировку из utf, которая является кодировкой, на котором написана программа, в unicode),
    то пришлось бы дописывать символы в коде юникода:
    [] + [u'\u2026'] + [u'\u2014'] + [u'\u2013']
    Можно не писать .decode("utf8"), а просто поставить u"текст"
    """
    punct = [i for i in ".,;:!?()[]{}`''\"@#$^&*+-|=~_∙«»…—–".decode("utf8")]
    without_punct = [w for w in tokens if not w in punct]
    print "Punctuation removed"
    return without_punct

def stem_pymorphy(tokens):
    morph = pymorphy2.MorphAnalyzer()
    stemmed = [morph.parse(token)[0].normal_form for token in tokens]
    print "Stemmed with Pymorphy"
    return stemmed

def stem_snowball(tokens):
    stemmer = SnowballStemmer("russian")
    stemmed = [stemmer.stem(token) for token in tokens]
    print "Stemmed with Snowball"
    return stemmed


def preprocess(text):
    return stem_pymorphy(remove_stopwords(remove_punct(tokenize_pattern(text))))


def clear_text(text):
    return " ".join(text.replace("\n", " ").replace("\r", " ").replace("\t", " ").split())