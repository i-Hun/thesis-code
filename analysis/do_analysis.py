# -*- coding: utf-8 -*-
from __future__ import division
from pymongo import MongoClient
from preprocess.preprocess import preprocess
from analysis import find_infrequient, remove_infrequent
from gensim import corpora, models
import os.path

db = MongoClient().thesis
raw_tokens = db.raw_tokens
# final_tokens = db.final_tokens


def update_db_for_remove_infreq():
    documents = [document["content"] for document in raw_tokens.find(fields={"content": 1})]

    infrequent_list = find_infrequient(documents)

    count = 1
    for doc in raw_tokens.find():
        new_content = remove_infrequent(doc["content"], infrequent_list)
        doc["content"] = new_content
        del doc["_id"]
        final_tokens.insert(doc)
        print "Удаление редких слов. Документ " + str(count)
        count += 1


def get_dictionary(mode):  # solo или docfreq
    """
    Словарь - список уникальных токенов, каждому из которых присвоен id. {0: "токен1", 2: "токен2" ...}
    Dictionary – a mapping between words and their integer ids.

    Dictionaries can be created from a corpus and can later be pruned according to document
    frequency (removing (un)common words via the Dictionary.filter_extremes() method),
    save/loaded from disk (via Dictionary.save() and Dictionary.load() methods),
    merged with other dictionary (Dictionary.merge_with()) etc.
    """

    file_path = "/home/hun/thesis-python/tmp/"

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



def get_corpus():
    """
    Создаёт вектор вида [(0, 1), (1, 1)], где в первых скобках - id токенов, которые встречаются в документе,
    а во вторых - их частота в данном конкретом документе.
    http://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary
    """
    file_path = "/home/hun/thesis-python/tmp/corpus.mm"
    corpus_exists = os.path.isfile(file_path)

    if corpus_exists:
        print "Загружаем корпус из файла " + file_path
        corpus = corpora.MmCorpus(file_path)
    else:
        print "Создаём и сохраняем корпус"
        texts = [document["content"] for document in raw_tokens.find(fields={"content": 1})]
        dictionary = get_dictionary("solo")
        """
        The function doc2bow() simply counts the number of occurences of each distinct word,
        converts the word to its integer word id and returns the result as a sparse vector.
        The sparse vector [(0, 1), (1, 1)]
        Если в словаре нет слова, то оно не учитывается
        """
        corpus = [dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(file_path, corpus)
    # print(corpus)
    return corpus

def do_lda():
    file_path = "/home/hun/thesis-python/tmp/lda.model"
    model_exists = os.path.isfile(file_path)
    if model_exists:
        lda = models.LdaModel.load(file_path)
    else:
        lda = models.ldamodel.LdaModel(corpus=get_corpus(), id2word=get_dictionary("solo"), num_topics=10)
        lda.save('/home/hun/thesis-python/tmp/lda.model')

    for i, topic in enumerate(lda.show_topics(lda.num_topics)):
        print i, topic

do_lda()