# -*- coding: utf-8 -*-
import moment
from datetime import datetime

from preprocess import preprocess
from analysis import most_common

from pymongo import MongoClient

client = MongoClient('localhost', 3001)

ngs = client.meteor.ngs


def find_min_date(collection_name):
    docs = collection_name.find().sort("date", 1)
    for doc in docs:
        if "date" in doc.keys():
            min_date = doc["date"]
            return min_date
        else:
            print "Нет даты"

def find_max_date(collection_name):
    docs = collection_name.find().sort("date", -1)
    for doc in docs:
        if "date" in doc.keys():
            max_date = doc["date"]
            return max_date
        else:
            print "Нет даты"

def split_by_month(collection_name):
    """
    Принимает на входе данные, возвращает массив этих данных, разбитых по месяцам
    """
    min_date = find_min_date(collection_name)
    max_date = find_max_date(collection_name)
    output = []

    while (moment.date(min_date).add(months=1).date < max_date):
        chunk = list(ngs.find({"$and": [{"date": {"$lt": moment.date(min_date).add(months=1).date}}, {"date": {"$gte": min_date}}]}).sort("date", 1))
        output.append(chunk)
        min_date = moment.date(min_date).add(months=1).date
    # TODO: возвращать не просто массив, а объект, где помимо данных будет их привязка к месяцу
    return output

for month in split_by_month(ngs):
    arr =[]
    for doc in month:
        arr.append(preprocess(doc["content"]))
    print most_common(arr)
    print "Конец месяца"
