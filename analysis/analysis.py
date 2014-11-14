# -*- coding: utf-8 -*-

from gensim import corpora, models, similarities


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
                print "Одиночный токен [{0}] встречается {1} раз".decode("utf8").format(token, c[token])
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


# # transformation between word-document co-occurrence matrix (integers) into a locally/globally weighted TF_IDF matrix
# # http://radimrehurek.com/gensim/tutorial.html#first-example
# tfidf = models.TfidfModel(corpus) # initialize (train) the transformation model
# tfidf.save('/tmp/ngs.tfidf_model')
#
# corpus_tfidf = tfidf[corpus]

def LDA(corpus, dictionary=None):

    """ LDA is yet another transformation from bag-of-words counts into a topic space
    Вообще применять LDA надо на основе bow, но некоторые делают это
    через tfidf (https://groups.google.com/forum/#!topic/gensim/OESG1jcaXaQ) """
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary)
    return lda
#
# lda = LDA(corpus, dictionary)
#
# for x in lda.show_topics(topics=lda.num_topics):
#     print x
#
#
# print(texts[1])
# print(corpus[1])
# print(lda[corpus[1]])
# TODO: сохранить модель

