# -*- coding: utf-8 -*-

import datetime
import requests
from pymongo import MongoClient
from pyquery import PyQuery as pq


client = MongoClient()
db = client.thesis
omskinform_links = db.omskinform_links
omskinform = db.omskinform

def parse_links():
    links = []
    for i in range(17, 308, 1):
        url = "http://www.omskinform.ru/all/" + str(i)

        response = requests.get(url)

        d = pq(response.text)

        newsitems = d(".n_news")

        for newsitem in newsitems:
            link = pq(newsitem).find(".n_cap_lnk").attr("href")
            links.append(link)
            print len(links), link
        print "_________________" + str(i) + "_________________"

    # omskinform_links.insert({"links": links})

parse_links()