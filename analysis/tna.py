# -*- coding: utf-8 -*-
from analysis import LDA, get_dictionary, get_corpus
from pymongo import MongoClient
from collections import defaultdict
import itertools
import igraph as ig
import cPickle as pickle
from settings import config
import math

db = MongoClient().thesis.final_db

dictionary = get_dictionary("solo")
corpus = get_corpus(dictionary)
model = LDA(dictionary, corpus, 50, "lda20/lda_training_50")
model.minimum_probability = 0
'''
Мне надо посчитать среднюю совместную вероятность всех пар тем
'''
def compute_joint_probs():
    joint_probs = defaultdict(int)
    general_probs = defaultdict(int)

    for i, document in enumerate(db.find()):
        doc_bow = dictionary.doc2bow(document["content"])
        topics_distr = model[doc_bow]

        pairs = itertools.combinations(topics_distr, 2)
        for pair in pairs:
            joint_probs[(pair[0][0], pair[1][0])] += pair[0][1] * pair[1][1]

        for topic, prob in topics_distr:
            general_probs[topic] += prob

    pickle.dump(general_probs, open("../output/general_probs.pickle", "wb"))
    pickle.dump(joint_probs, open("../output/joint_probs.pickle", "wb"))


general_probs = pickle.load(open("../output/general_probs.pickle", "rb"))
joint_probs = pickle.load(open("../output/joint_probs.pickle", "rb"))

g = ig.Graph()

# Устанавливаем вершины
for topic, prob in general_probs.items():
    g.add_vertex(topic)

# Устанавиваем среднюю вероятность
for idx, v in enumerate(g.vs):
    v["mean_prob"] = general_probs[v["name"]]

for topics_pair, joint_prob in joint_probs.items():
    g.add_edge(topics_pair[0], topics_pair[1], joint_prob=joint_prob)

visual_style = {}
visual_style["vertex_size"] = [mean_prob/20 for mean_prob in g.vs["mean_prob"]]
visual_style["layout"] = g.layout_circle()
visual_style["vertex_color"] = "grey"
visual_style["edge_width"] = [joint_prob**1.6/200 for joint_prob in g.es["joint_prob"]]
visual_style["vertex_label_angle"] = 0
#visual_style["vertex_label_dist"] = 30
visual_style["vertex_label_size"] = 16
visual_style["vertex_label"] = [name for name in g.vs["name"]]
visual_style["bbox"] = (1200, 1200)
visual_style["margin"] = 100
ig.plot(g, **visual_style)