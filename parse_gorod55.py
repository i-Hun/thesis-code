# -*- coding: utf-8 -*-

import datetime
import requests
import json
from pymongo import MongoClient
from preprocess import remove_urls, get_text


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

    return [get_text(remove_urls(item["CommentText"])) for item in response.json()["Result"] if item["Status"] == "Claim" and get_text(remove_urls(item["CommentText"])) != ""]


def get_article():
    params = json.dumps({"SessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
              "ID": "2adfd4aa-c7ff-48de-efe5-70aca5eda3b1",
              "IsRequest": True,
              "Type": "Search",
              "FullTextSearchRequest": "",
              "Domain": "News",
              "MessageMapKey": "news_Search",
              "Order": [{"Field": "PrimaryOrder", "Reverse": True}],
              "Ranges": {"PrimaryOrder": {"left": "2013-09-01T00:00:00", "right": "2014-09-01T23:59:00"}},
              "Page": 1,
              "Count": 100,  # максимальное количество 100
              "Characs": {},
              "UseGzip": False})

    response = requests.post("http://beta.api.gorod55.ru/search/news", params)

    count_articles = 1
    for page in range(1, int(response.json()["ResultCount"])/100):
        params = json.dumps({"SessionID": "b7e39379-79f2-42d3-ea1e-1131974a6fab",
                  "ID": "2adfd4aa-c7ff-48de-efe5-70aca5eda3b1",
                  "IsRequest": True,
                  "Type": "Search",
                  "FullTextSearchRequest": "",
                  "Domain": "News",
                  "MessageMapKey": "news_Search",
                  "Order": [{"Field": "PrimaryOrder", "Reverse": True}],
                  "Ranges": {"PrimaryOrder": {"left": "2013-09-01T00:00:00", "right": "2014-09-01T23:59:00"}},
                  "Page": page,
                  "Count": 100,  # максимальное количество 100
                  "Characs": {},
                  "UseGzip": False})

        response = requests.post("http://beta.api.gorod55.ru/search/news", params)

        for item in response.json()["Result"]:
            title = get_text(item["Title"])
            content = get_text(item["Description"])
            url = "http://gorod55.ru/news/article/" + item["EntityID"]
            date = datetime.datetime.strptime((item["PrimaryOrder"])[0:10], "%Y-%m-%d")  # 2014-08-28T17:40:00
            comments = get_comments(item["EntityID"])
            comments_count = len(comments)

            print count_articles, title, content, url, date
            print "++++++++++++++++++++++++++++++++++++++++++++++++++"
            count_articles += 1
            count = 1
            for comment in comments:
                print count, comment
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



#get_article()
