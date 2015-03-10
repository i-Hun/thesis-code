# -*- coding: utf-8 -*-

from gensim import corpora, models
import os.path
from pymongo import MongoClient
db = MongoClient().thesis
raw_tokens = db.raw_tokens


def find_infrequient(documents):
    """ На входе принимаем токенизированный список документов
    вида [[токен1, токен2], [токен1, токен3]]

    Находим слова, которые встречаются меньше определённого количества раз

    98262 токенов, которые встречаются 2 или 1 раз
    49279 -- 1 раз
    54552 токенов, которые встречаются только в одном документе
    всего 118806
    """

    from collections import Counter

    c = Counter(token for document in documents for token in document)

    infrequient = []

    # Single line: [[token for token in document if c[token] > 1] for document in documents]
    for document in documents:
        for token in document:
            if c[token] <= 1:
                print "Токен [{0}] встречается {1} раз".decode("utf8").format(token, c[token])
                infrequient.append(token)

    print "Общее количество токенов {0}. Найдёно {1} редких токенов".format(len(c), len(infrequient))
    return infrequient


def remove_infrequent(doc, infrequent_list):
    """doc - массив токенов"""
    return [word for word in doc if word not in infrequent_list]


def most_common(documents, count=10):
    """ На входе принимаем токенизированный список документов
    вида [[токен1, токен2], [токен1, токен3]]"""

    from collections import Counter
    c = Counter(token for document in documents for token in document)

    # TODO: не просто вывести в консоль, но возвратить структуру данных, с которой можно дальше работать
    for val in c.most_common(count):
        print '{0}: {1}'.format(val[0].encode('utf-8'), val[1])


def get_dictionary(mode):  # solo или docfreq
    """
    Словарь - список уникальных токенов, каждому из которых присвоен id. {0: "токен1", 2: "токен2" ...}
    Dictionary – a mapping between words and their integer ids.

    Dictionaries can be created from a corpus and can later be pruned according to document
    frequency (removing (un)common words via the Dictionary.filter_extremes() method),
    save/loaded from disk (via Dictionary.save() and Dictionary.load() methods),
    merged with other dictionary (Dictionary.merge_with()) etc.
    """

    file_path = "../output/"

    if mode == "solo":
        file_path += "dictionary_solo.dict"
    elif mode == "docfreq":
        file_path += "dictionary_docfreq.dict"
    else:
        raise Exception("Укажите режим -- solo или docfreq")

    dict_exists = os.path.isfile(file_path)

    if dict_exists:
        print "Загружаем словарь из файла " + file_path
        dictionary = corpora.Dictionary.load(file_path)
    else:
        print "Создаём и сохраняем словарь"
        if mode == "solo":
            """
            Создаёт словарь без токенов, которые встречаются только один раз
            Работает долго.
            """
            texts = [document["content"] for document in raw_tokens.find(fields={"content": 1})]
            dictionary = corpora.Dictionary(texts)
            solo_tokens = find_infrequient(texts)
            solo_ids = [id for id, token in dictionary.iteritems() if token in solo_tokens]
            dictionary.filter_tokens(solo_ids)
            dictionary.compactify()
        elif mode == "docfreq":
            """
            Создаёт словарь без токенов, которые встречаются только в одном документе
            Работает быстро.
            """
            texts = [document["content"] for document in raw_tokens.find(fields={"content": 1})]
            dictionary = corpora.Dictionary(texts)
            in_one_doc_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
            print "Найдено {0} токенов, которые встречаются только в одном документе".format(len(in_one_doc_ids))
            dictionary.filter_tokens(in_one_doc_ids)
            dictionary.compactify()
        else:
            raise Exception("Укажите режим -- solo или docfreq")
    dictionary.save(file_path)
    print(dictionary)
    return dictionary


def get_corpus(dictionary):
    """
    Создаёт вектор вида [(0, 1), (1, 1)], где в первое значение в скобках - id токенов, которые встречаются в документе,
    а во вторых - их частота в данном конкретом документе.
    http://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary
    """
    file_path = "../output/corpus_metadata.mm"
    corpus_exists = os.path.isfile(file_path)

    if corpus_exists:
        print "Загружаем корпус из файла " + file_path
        corpus = corpora.MmCorpus(file_path)
    else:
        print "Создаём и сохраняем корпус"
        texts = [document["content"] for document in raw_tokens.find(fields={"content": 1})]
        """
        The function doc2bow() simply counts the number of occurences of each distinct word,
        converts the word to its integer word id and returns the result as a sparse vector.
        The sparse vector [(0, 1), (1, 1)]
        Если в словаре нет слова, то оно не учитывается
        """
        corpus = [dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(file_path, corpus, metadata=True)
    # print(corpus)
    return corpus


def LDA(dictionary, corpus, num_topics, version, passes=1):
    print "Построение модели LDA"
    file_path = "../output/lda/{version}.model".format(version=version)
    model_exists = os.path.isfile(file_path)
    if model_exists:
        lda = models.LdaModel.load(file_path)
    else:
        lda = models.LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=passes)
        lda.save(file_path)
    return lda

def hLDA(dictionary, corpus):
    print "Построение модели hLDA"
    file_path = "../output/hlda/hlda.model"
    model_exists = os.path.isfile(file_path)
    if model_exists:
        hlda = models.HdpModel.load(file_path)
    else:
        hlda = models.hdpmodel.HdpModel(corpus=corpus, id2word=dictionary)
        hlda.save(file_path)
    return hlda