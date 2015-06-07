# -*- coding: utf-8 -*-
from analysis import LDA, get_dictionary, get_corpus, hLDA
import random
import matplotlib.pyplot as plt

import logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

import numpy as np
from settings import config

from matplotlib import rc
font = {
    'family': config.get("tex_font_family"),
    'weight': 'normal',
    'size': config.get("tex_font_size")
}
rc('font', **font)

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)

# hLDA
# hlda = hLDA(dictionary, corpus)
# for i, topic in enumerate(hlda.show_topics(topics=-1)):
#     print i+1, topic

#MALLET
# for num_topics in range(60, 65, 10):
#     model = models.LdaMallet('~/mallet-2.0.7/bin/mallet', corpus=corpus, num_topics=num_topics, id2word=dictionary)
#     model.save("../output/lda/lda_mallet/lda_mallet_{num_topics}.model".format(num_topics=num_topics))
#     print "\n \n \nFUKKEN SAVED!!! Не проморгай \n \n \n "


def mallet_plot():
    ## Строим график из данных Mallet
    topics = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    perp = [514.1302184469, 525.0241590983, 534.4977260582, 538.5513127672, 541.8989344152, 541.0094559616, 538.4206752508, 535.3505225192, 532.7629698852, 533.9200808978, 540.3049166531, 531.4757292891, 538.0214941918, 546.4364835315, 538.0214941918, 540.9982061032, 532.1429352736, 535.5732148468, 536.4983783528, 539.0330790911]
    plt.plot(topics, perp, 'o-')
    plt.ylabel(u'Перплексия')
    plt.xlabel(u'Количество тем')
    plt.grid(True)
    plt.xlim(0, 105)
    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "perplexity_mallet." + ext,
                    format=ext, bbox_inches='tight', dpi=1200)


def perplexity():
    # split into train and test - random sample, but preserving order
    perwordbound_list = []
    perplexity2_list = []
    topics_list = []

    train_size = int(round(len(corpus)*0.9))
    train_index = sorted(random.sample(xrange(len(corpus)), train_size))
    test_index = sorted(set(xrange(len(corpus)))-set(train_index))
    train_corpus = [corpus[i] for i in train_index]
    test_corpus = [corpus[j] for j in test_index]


    for num_topics in range(5, 101, 5):
        model = LDA(dictionary, train_corpus, num_topics, "lda20/lda_training_{num_topics}"
                    .format(num_topics=str(num_topics)), passes=20)
        perwordbound = model.log_perplexity(test_corpus)
        perplexity2 = np.exp2(-perwordbound)

        perwordbound_list.append(perwordbound)
        perplexity2_list.append(perplexity2)
        topics_list.append(num_topics)

    plt.plot(topics_list, perwordbound_list, 'o-')
    plt.ylabel(u'Per word bound')
    plt.xlabel(u'Количество тем')
    plt.grid(True)
    plt.xlim(0, 105)
    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "perplexity_perwordbound." + ext,
                    bbox_inches='tight', format=ext, dpi=1200)
    plt.close()


    plt.plot(topics_list, perplexity2_list, 'o-')
    plt.ylabel(u'Перплексия')
    plt.xlabel(u'Количество тем')
    plt.grid(True)
    plt.xlim(0, 105)
    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "perplexity_exp2." + ext,
                    format=ext, bbox_inches='tight', dpi=1200)
    plt.close()

perplexity()
