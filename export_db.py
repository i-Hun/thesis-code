# -*- coding: utf-8 -*-
from __future__ import division
from lxml import etree
from pymongo import MongoClient
from settings import config

from math import fmod

db = MongoClient().thesis.merged

def single_file():
    corpus = etree.Element("corpus")

    for doc in db.find():
        document = etree.SubElement(corpus, "document")
        etree.SubElement(document, "title").text = doc["title"]
        etree.SubElement(document, "content").text = doc["content"]
        etree.SubElement(document, "date").text = str(doc["date"])
        etree.SubElement(document, "url").text = doc["url"]
        etree.SubElement(document, "source").text = doc["source"]
        comments = etree.SubElement(document, "comments", amount=str(len(doc["comments"])))

        for comment in doc["comments"]:
            etree.SubElement(comments, "comment").text = comment

    xml_str = etree.tostring(corpus, pretty_print=True)

    outFile = open("{0}/Thesis/omsk_media.xml".format(config.get("home_path")), 'w')
    outFile.write(xml_str)
    outFile.close()

def file_every_1000():
    for num, doc in enumerate(db.find()):
        if fmod(num, 1000) == 0:
            corpus = etree.Element("corpus")
            begin = num
            end = begin + 1000
            if end > db.find().count():
                end = db.find().count() - 1
            print "begin, end ", begin, end

            for doc in db.find()[begin:end]:
                document = etree.SubElement(corpus, "document")
                etree.SubElement(document, "title").text = doc["title"]
                etree.SubElement(document, "content").text = doc["content"]
                etree.SubElement(document, "date").text = str(doc["date"])
                etree.SubElement(document, "url").text = doc["url"]
                etree.SubElement(document, "source").text = doc["source"]
                comments = etree.SubElement(document, "comments", amount=str(len(doc["comments"])))

                for comment in doc["comments"]:
                    etree.SubElement(comments, "comment").text = comment

            xml_str = etree.tostring(corpus, pretty_print=True)

            with open("{0}/Thesis/omsk_media_{1}-{2}.xml".format(config.get("home_path"), begin, end), 'w') as outFile:
                outFile.write(xml_str)