# -*- coding: utf-8 -*-

import datetime
import requests
import json
from pymongo import MongoClient
from pyquery import PyQuery as pq

client = MongoClient()
db = client.thesis
gorod55 = db.gorod55


def get_comments(id):
    params = json.dumps({"SessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
              "ID": "f66cc5ed-efea-46c0-c1cc-0d2d010dc62d",
              "IsRequest": True,
              "Type": "GetComments",
              "MessageMapKey": "GetComments",
              "RubricName": "news",
              "EntityID": id,
              "UserSessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
              "UseGzip": False})
    response = requests.post("http://beta.api.gorod55.ru/realty", params)

    return [item["CommentText"] for item in response.json()["Result"] if item["Status"] == "Claim" and item["CommentText"] != ""]


def get_articles():
    count_articles = 1

    params = json.dumps({"SessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
                             "ID": "de0b2895-1da4-4c49-c61d-eb890edcdf75",
                             "IsRequest": True,
                             "Type": "Search",
                             "FullTextSearchRequest": "",
                             "Domain": "News",
                             "MessageMapKey": "news_Search",
                             "Order": [{"Field": "PrimaryOrder", "Reverse":True}],
                             "Ranges": {"PrimaryOrder": {"left": "2013-09-01T00:00:00", "right": "2014-09-01T23:59:00"}},
                             "Count": 100,
                             "Page": 0,
                             "UseGzip": False})

    response = requests.post("http://beta.api.gorod55.ru/search/news", params)
    pages_count = int(response.json()["ResultCount"])/100

    for page in range(0, pages_count + 1):
        print "PAGE: " + str(page) + "/" + str(pages_count)
        params = json.dumps({"SessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
                             "ID": "de0b2895-1da4-4c49-c61d-eb890edcdf75",
                             "IsRequest": True,
                             "Type": "Search",
                             "FullTextSearchRequest": "",
                             "Domain": "News",
                             "MessageMapKey": "news_Search",
                             "Order": [{"Field": "PrimaryOrder", "Reverse":True}],
                             "Ranges": {"PrimaryOrder": {"left": "2013-09-01T00:00:00", "right": "2014-09-01T23:59:00"}},
                             "Count": 100,
                             "Page": page,
                             "UseGzip": False})

        response = requests.post("http://beta.api.gorod55.ru/search/news", params)

        for item in response.json()["Result"]:
            title = item["Title"]
            content = pq(item["Description"]).text()
            url = "http://gorod55.ru/news/article/" + item["EntityID"]
            date = datetime.datetime.strptime((item["PrimaryOrder"])[0:10], "%Y-%m-%d")  # 2014-08-28T17:40:00
            comments = get_comments(item["EntityID"])
            comments_count = len(comments)

            print count_articles, title, content, url, date
            print "Comments: "
            count_articles += 1
            count = 1
            for comment in comments:
                print "     " + str(count), comment
                count += 1
            print comments_count

            doc = {
                "title": title,
                "content": content,
                "url": url,
                "date": date,
                "commentsCount": comments_count,
                "comments": comments
            }
            gorod55.insert(doc)

# get_articles()
