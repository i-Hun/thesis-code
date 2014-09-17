# -*- coding: utf-8 -*-

import datetime
import requests
from pymongo import MongoClient
from pyquery import PyQuery as pq


client = MongoClient()
db = client.thesis
ngs55_links = db.ngs55_links
ngs55 = db.ngs55

def parse_links():
    links = []
    for i in range(250, 11, -1):
        url = "http://ngs55.ru/news/page/" + str(i)

        response = requests.get(url)

        d = pq(response.text)

        newsitems = d(".news-items>.article h3 a")

        for newsitem in newsitems:
            link = pq(newsitem).attr("href")
            links.append(link)
            print len(links), link
        print "_________________" + str(i) + "_________________"

    ngs55_links.insert({"links": links})



def parse_articles():
    count = 1
    for link in ngs55_links.find_one()['links']:

        response = requests.get(link)
        d = pq(response.text)

        content = d(".nn-article-text").text()

        title = d(".nn-article-header").text()

        row_date = d(".nn-article-date").text()
        date = datetime.datetime(int(row_date.split(".")[2]), int(row_date.split(".")[1]), int(row_date.split(".")[0]))

        if d(".comments-title"):
            comments_count = int(re.findall(r'\d+', d(".comments-title").text())[0])
            print("Comments", comments_count, link)
        else:
            comments_count = 0
            print("Comments are closed", link)


        comments = [pq(comment).text() for comment in d(".extended_comment__content")]

        doc = {
            "title": title,
            "content": content,
            "url": link,
            "date": date,
            "commentsCount": comments_count,
            "comments": comments
        }

        print count, link, date, comments_count, len(comments)
        ngs55.insert(doc)

        count += 1


# parse_articles()