# -*- coding: utf-8 -*-

from gensim import corpora, models, similarities

from pymongo import MongoClient
client = MongoClient('localhost', 3001)

ngs = client.meteor.ngsPreprocessed

doc = ngs.find_one()["url"]

# Создаём вектор
# http://radimrehurek.com/gensim/tut1.html
texts = [text["content"] for text in ngs.find()]

## Словарь - список уникальных токенов, каждому из которых присвоен id. {"токен": 0, "токен2": 1 ...}
dictionary = corpora.Dictionary(texts)

# dictionary.save('/tmp/ngs.dict')
# dictionary = corpora.Dictionary.load('/tmp/ngs.dict')

# for t, i in dictionary.token2id.iteritems():
#     print t, i

#TODO удалить токены (или слова до токенизации? Ответ: после), которые встречаются только один раз

# Создаёт вектор вида [(0, 1), (1, 1)], где в первых скобках - id токенов, которые встречаются в документе, а во вторых - их частота.
# http://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary
corpus = [dictionary.doc2bow(text) for text in texts]
# corpus = corpora.MmCorpus.load('/tmp/ngs.mm')

corpora.MmCorpus.serialize('/tmp/ngs.mm', corpus)


# transformation between word-document co-occurrence matrix (integers) into a locally/globally weighted TF_IDF matrix
# http://radimrehurek.com/gensim/tutorial.html#first-example
tfidf = models.TfidfModel(corpus) # initialize (train) the transformation model
tfidf.save('/tmp/ngs.tfidf_model')

# LDA
lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary)

for x in lda.print_topics():
    print x