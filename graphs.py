# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from settings import config

from matplotlib import rc
font = {
    'family': config.get("tex_font_family"),
    'weight': 'normal',
    'size': config.get("tex_font_size")
}
rc('font', **font)


def doc_number():
    width = 0.8
    data = {
        "bk55": 14078,
        "gorod55": 6302,
        "ngs55": 4780,
        "omskinform": 8727
    }
    sources_x = np.arange(len(data))
    numbers = [number for source, number in data.items()]

    fig, ax = plt.subplots()
    ax.set_xlabel(u'Источник')
    ax.set_ylabel(u'Количество статей')
    rects = ax.bar(sources_x, numbers, width)
    plt.xticks(sources_x + 0.4, data.keys())

    for rect, label in zip(rects, data.keys()):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height + 5, height, ha='center', va='bottom')

    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "doc_number." + ext, bbox_inches='tight', format=ext, dpi=1200)
    plt.show()


def avg_comments():
    width = 0.8
    data = {
        "bk55": 8.5272094345,
        "gorod55": 10.6726493011,
        "ngs55": 9.88509836752,
        "omskinform": 2.71181391085
    }

    sources = data.keys()

    data = [(source, round(avg, 2)) for source, avg in sorted(data.items(), key=lambda x: x[1])]
    sources_x = np.arange(len(data))
    numbers = [number for source, number in data]

    fig, ax = plt.subplots()
    ax.set_xlabel(u'Источник')
    ax.set_ylabel(u'Среднее количество комментариев')
    rects = ax.bar(sources_x, numbers, width)
    plt.xticks(sources_x + 0.4, sources)

    for rect, label in zip(rects, sources):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height, height, ha='center', va='bottom')

    for ext in config.get("tex_image_format"):
        plt.savefig(config.get("tex_image_path") + "avg_comments." + ext, bbox_inches='tight', format=ext, dpi=1200)
    plt.show()

avg_comments()