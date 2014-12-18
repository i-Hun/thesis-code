# -*- coding: utf-8 -*-
from __future__ import division

import logging
log = logging.getLogger('Preprocess')
log.setLevel(logging.INFO)

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer

import pymorphy2

from pattern.en import tokenize

import re

from nltk.corpus import stopwords


def replace_non_breaking_space(string):
    return string.replace(u'\xa0', u' ')


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
    log.debug("Tokenize with regexp")
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
    log.debug("Tokenize with Pattern")
    return tokens


def remove_urls(text):
    without_urls =  re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
    log.debug("URLs removed")
    return without_urls


def remove_stopwords(tokens):
    stopwords_ru = stopwords.words('russian')
    additional_stopwords = ["это", "который", "некоторый", "некоторые", "свой", "также", "однако", "тот", "быть", "такой", "другой", "стать", "однако", "етот", "наш", "говорить", "мы", "год", "очень", "весь", "ещё", "каждый", "мочь", "самый", "сказать", "хотеть", "просто", "оно", "ваш"]
    additional_stopwords = additional_stopwords + ["омск-информ", "omskinform.ru", "omskinform", "бк55", "bk55.ru", "bk55", "город55", "gorod55.ru", "gorod55", "нгс", "ngs55.ru"]
    additional_stopwords = [unicode(stopword, 'utf-8') for stopword in additional_stopwords]
    stopwords_ru.extend(additional_stopwords)
    filtered_tokens = [w for w in tokens if not w in stopwords_ru]
    log.debug("Stopwords removed")
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
    log.debug("Punctuation removed")
    return without_punct


def stem_pymorphy(tokens):
    morph = pymorphy2.MorphAnalyzer()
    stemmed = [morph.parse(token)[0].normal_form for token in tokens]
    log.debug("Stemmed with Pymorphy")
    return stemmed


def stem_snowball(tokens):
    stemmer = SnowballStemmer("russian")
    stemmed = [stemmer.stem(token) for token in tokens]
    log.debug("Stemmed with Snowball")
    return stemmed


def replace_tokens(tokens, replace_dict):
    return [replace_dict[token] if token in replace_dict.keys() else token for token in tokens]


#TODO сделать цепочки функций через декораторы или классы
def preprocess(text):
    text = text.lower()
    text = replace_non_breaking_space(text)
    tokens = tokenize_pattern(text)
    tokens = remove_punct(tokens)
    tokens = stem_pymorphy(tokens)
    tokens = remove_stopwords(tokens)
    tokens = replace_tokens(tokens, {
                                        u"ул": u"улица",
                                        u"омский": u"омск",
                                        u"рф": u"россия",
                                        u"российский": u"россия",
                                        u"етот": u"этот",
                                        U"парка": u"парк",
                                        u"ст": u"статья",
                                        u"деньга": u"деньги",
                                        u"расина": u"расин"
                                    })
    return tokens


def clear_text(text):
    return " ".join(text.replace("\n", " ").replace("\r", " ").replace("\t", " ").split())


def remove_words(collection, stopwords_list):
    """
    Удаление списка слов из поля content выбранной коллекции.
    Тип поля content -- список слов
    """
    stopwords_list = [unicode(stopword, 'utf-8') for stopword in stopwords_list]
    for doc in collection.find(fields={"content": 1, "_id": 1}):
        if not set(stopwords_list).isdisjoint(set(doc["content"])):
            new_content = [w for w in doc["content"] if not w in stopwords_list]
            collection.update({"_id": doc["_id"]}, {"$set": {"content": new_content}})


def replace_words(collection, replace_dict):
    """
    Заменя слов из поля content выбранной коллекции по указанному словарю.
    Тип поля content -- список слов
    """
    for doc in collection.find(fields={"content": 1, "_id": 1}):
        new_content = replace_tokens(doc["content"], replace_dict)
        collection.update({"_id": doc["_id"]}, {"$set": {"content": new_content}})
