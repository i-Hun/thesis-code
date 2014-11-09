# -*- coding: utf-8 -*-

from gensim import corpora, models, similarities


def remove_alone(documents):
    """ На входе принимаем токенизированный список документов
    вида [[токен1, токен2], [токен1, токен3]]"""

    from collections import Counter

    c = Counter(token for document in documents for token in document)

    docs = []
    single_count = 0

    # Single line: [[token for token in document if c[token] > 1] for document in documents]
    for document in documents:
        doc = []
        for token in document:
            if c[token] < 2:
                print "Одиночный токен: {0}".decode("utf8").format(token)
                single_count += 1
            else:
                doc.append(token)
        docs.append(doc)

    print "Найдёно {0} уникальных токенов".format(single_count)
    return docs


def most_common(documents, count=10):
    """ На входе принимаем токенизированный список документов
    вида [[токен1, токен2], [токен1, токен3]]"""

    from collections import Counter
    c = Counter(token for document in documents for token in document)

    # TODO: не просто вывести в консоль, но возвратить структуру данных, с которой можно дальше работать
    for val in c.most_common(count):
        print '{0}: {1}'.format(val[0].encode('utf-8'), val[1])
#

# not_alone = remove_alone(texts)
# most_common(not_alone, 20)
#
# ## Словарь - список уникальных токенов, каждому из которых присвоен id. {"токен": 0, "токен2": 1 ...}
# dictionary = corpora.Dictionary(texts)
#
# # dictionary.save('/tmp/ngs.dict')
# # dictionary = corpora.Dictionary.load('/tmp/ngs.dict')
#
#
# # Создаёт вектор вида [(0, 1), (1, 1)], где в первых скобках - id токенов, которые встречаются в документе, а во вторых - их частота.
# # bag-of-words integer counts
# # http://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary
# corpus = [dictionary.doc2bow(text) for text in texts]
# # corpus = corpora.MmCorpus.load('/tmp/ngs.mm')
#
# corpora.MmCorpus.serialize('/tmp/ngs.mm', corpus)
#
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

