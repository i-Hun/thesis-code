# -*- coding: utf-8 -*-
import moment
import datetime


from preprocess import preprocess
from analysis import most_common
from nltk.probability import FreqDist

from pymongo import MongoClient

client = MongoClient('localhost', 3001)

ngs = client.meteor.ngs

def remove_without_date(collection_name):
    print "Удалено документов без даты: \n" + str(collection_name.remove({"date": None})["n"]) + "\n--------------------------------------"

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
        output.append((chunk, min_date))
        min_date = moment.date(min_date).add(months=1).date
    # TODO: возвращать не просто массив, а объект, где помимо данных будет их привязка к месяцу
    return output

remove_without_date(ngs)

for month in split_by_month(ngs):
    print month[1]

# for month in split_by_month(ngs):
#     arr =[]
#     for doc[0] in month:
#         arr.append(preprocess(doc["content"]))
#     print most_common(arr)
#     print "Конец месяца"

def averange_count(collection_name):
    unic_dates = list(set([datetime.datetime.date(record["date"]) for record in collection_name.find()]))
    return collection_name.find().count() / len(unic_dates)

def count_by_day(collection_name):

    # Берём каждую дату, оставляем только день, год и месяц, удаляем повторяющиеся дни
    unic_dates = list(set([datetime.datetime.date(record["date"]) for record in collection_name.find()]))

    # Сортируем список уникальным дат по возростанию
    unic_dates.sort()

    # Список, в котором содержится количество документов за месяц
    count = []

    for day in unic_dates:

        start_day = datetime.datetime.combine(day, datetime.time())
        end_day = datetime.datetime.combine(day, datetime.time(23, 59, 59))

        count.append(collection_name.find({"$and": [{"date": {"$lt": end_day}}, {"date": {"$gte": start_day}}]}).count())

    return dict([('date', unic_dates), ('count', count)])

def count_by_day_graph(collection_name):
    # TODO: выделить на графике выходные дни
    import numpy as np
    from bokeh.plotting import output_file, hold, figure, line, curplot, grid, show
    a = count_by_day(collection_name)
    output_file("output/count_by_day_graph.html", title="count_by_day_graph")

    hold()

    figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,previewsave", plot_width=1800)

    line(np.array(a["date"], 'M64'), a['count'], color='#A6CEE3', legend='Количество статей')
    line(np.array(a["date"], 'M64'), [averange_count(collection_name)] * len(a["date"]), color='#ff0000', legend='Среднее количество статей')

    curplot().title = "Количество статей по дням"
    grid().grid_line_alpha=0.3

    show()

count_by_day_graph(ngs)



print averange_count(ngs)