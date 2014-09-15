# -*- coding: utf-8 -*-

import datetime
import requests
from pymongo import MongoClient
from preprocess import remove_urls, get_text, clear_text
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


client = MongoClient()
db = client.thesis
bk55_links = db.bk55_links
bk55 = db.bk55


def month_by_name(row_date):
    if row_date.split()[1] == u"января":
        return 1
    elif row_date.split()[1] == u"февраля":
        return 2
    elif row_date.split()[1] == u"марта":
        return 3
    elif row_date.split()[1] == u"апреля":
        return 4
    elif row_date.split()[1] == u"мая":
        return 5
    elif row_date.split()[1] == u"июня":
        return 6
    elif row_date.split()[1] == u"июля":
        return 7
    elif row_date.split()[1] == u"августа":
        return 8
    elif row_date.split()[1] == u"сентября":
        return 9
    elif row_date.split()[1] == u"октября":
        return 10
    elif row_date.split()[1] == u"ноября":
        return 11
    elif row_date.split()[1] == u"декабря":
        return 12

def parse_links():
    links = []
    for i in range(29, 656):
        url = "http://bk55.ru/news/page/" + str(i)

        response = requests.get(url)

        soup = BeautifulSoup(response.text)

        newsitems = soup.findAll("div", {"class": "newsitem"})

        for newsitem in newsitems:
            row_link = newsitem.find("div", {"class": "n-head"}).find("a").get('href')

            if row_link[0:4] != "http":
                if row_link[0:1] == "/":
                    link = "http://www.bk55.ru" + row_link
                    links.append(link)
                    print len(links), link
                else:  # urlы из раздела kolumnistika представлены без слеша
                    link = "http://www.bk55.ru/" + row_link
                    links.append(link)
                    print len(links), link
            else:
                if row_link[0:18] == "http://www.bk55.ru":
                    links.append(row_link)
                    print len(links), row_link
    print len(links)
    bk55_links.insert({"links": links})

def parse_articles():
    count = 1
    for link in bk55_links.find_one()['links'][2727:]:
        print link
        response = requests.get(link)

        d = pq(response.text)

        # для таких http://www.bk55.ru/news/article/38028/
        # и таких http://www.bk55.ru/mc2/news/article/3724 статей надо менять образец
        if len(d("#main>div:first-child>div")) == 4 and len(d("div#main")) == 1:
            if d("#main>div:first-child>div:last").hasClass("commet_text"):
                row_date = d("#main>div:first-child>div:nth-child(3)").text()
            else:
                row_date = d("#main>div:first-child>div:nth-child(4)").text()  # 02 сентября 2013 — 09:41
        elif len(d("#main>div:first-child>div")) == 3 and len(d("div#main")) == 1:
            row_date = d("#main>div:first-child>div:nth-child(3)").text()  # 02 сентября 2013 — 09:41
        elif len(d("div#main")) == 2:  # http://www.bk55.ru/kolumnistika/article/37410/
            row_date = d("#main #main>div:first-child>div:nth-child(2)>div>div").text()

        date = datetime.datetime(int(row_date.split()[2]), month_by_name(row_date), int(row_date.split()[0]))


        title = d("#main h1").text()


        # Удаляем подписи к изображениям. Чаще всего этой копирайт: автор или сайт, с которого взято фото
        if d("#divcontnews table img"):
            content = d("#divcontnews")
            content = content.remove("table").text()
        else:
            content = d("#divcontnews").text()


        if d("#main>#commcount") or d("#main>div>.comment"):
            if link[0:22] == "http://www.bk55.ru/mc2":
                comments_count = int(d("#main>#commcount").text().replace(u"Комментариев:", ""))
            else:
                comments_count = int(d("#main>div>.comment").text())
        else:
            comments_count = 0
            print "Комментирование запрещено"


        if d(".comment-text"):
            commentsPyquery = d(".comment-text>div:nth-child(2)")
            comments = [clear_text(pq(comment).text()) for comment in commentsPyquery]
        else:
            comments = []

        print count, content, title

        doc = {
            "title": title,
            "content": content,
            "url": link,
            "date": date,
            "commentsCount": comments_count,
            "comments": comments
        }
        bk55.insert(doc)
        count += 1

# удалить p, li { white-space: pre-wrap; } в начале некоторых записей
# count = 1
# for doc in bk55.find({'content': {'$regex': 'p, li { white-space: pre-wrap;'}}):
#     old_content = doc["content"]
#     new_content = old_content.replace("p, li { white-space: pre-wrap;", "")
#     bk55.update({"url": doc["url"]}, {"$set": {"content": new_content}})
#     for i in bk55.find({'content': {'$regex': 'Товарищ Пауэр, не плюйтесь, пожалуйста!'}}):
#         print i["url"]
#     count += 1
