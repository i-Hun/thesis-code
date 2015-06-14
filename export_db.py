# -*- coding: utf-8 -*-

from lxml import etree
from pymongo import MongoClient
from settings import config

db = MongoClient().thesis.merged

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