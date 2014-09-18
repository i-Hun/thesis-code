# -*- coding: utf-8 -*-

import datetime
import requests
from pymongo import MongoClient
from pyquery import PyQuery as pq

import gevent
from gevent import monkey, pool
monkey.patch_all()


client = MongoClient()
db = client.thesis
omskinform_links = db.omskinform_links
omskinform = db.omskinform

def parse_links():
    links = []
    for i in range(18, 309, 1):
        url = "http://www.omskinform.ru/all/" + str(i)

        response = requests.get(url)

        d = pq(response.text)

        newsitems = d(".n_news")

        for newsitem in newsitems:
            link = pq(newsitem).find(".n_cap_lnk").attr("href")
            links.append(link)
            print len(links), link
        print "_________________" + str(i) + "_________________"

    omskinform_links.insert({"links": links})


jobs = []
p = pool.Pool(10)

def parse_article(url):
    response = requests.get(url)

    if response.status_code == 200:
        d = pq(response.text)
        title = d(".n_cap_lnk_one").text()

        content = d(".n_text_lnk").text()

        row_date = d(".n_date .f_right").text()
        date = datetime.datetime(int("20" + row_date[6:8]), int(row_date[3:5]), int(row_date[0:2]))

        comments_top = [pq(comment).children("span").text() for comment in d(".cmm_message_text")]
        comments_answer = [pq(comment).children("span").remove("i").text() for comment in d(".cmm_message_text_ans")]  # Удаляем цитированный текст (выделен курсивом)
        comments = comments_top + comments_answer

        comments_count = len(comments)

        doc = {
            "title": title,
            "content": content,
            "url": url,
            "date": date,
            "commentsCount": comments_count,
            "comments": comments
        }
        print url, title, len(comments)

        omskinform.insert(doc)
    else:
        raise Exception("Response status code is " + response.status_code + ". URL: " + response.url)

for url in omskinform_links.find_one()['links']:
    jobs.append(p.spawn(parse_article, url))

# gevent.joinall(jobs)