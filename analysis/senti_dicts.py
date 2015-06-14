# -*- coding: utf-8 -*-

import pymorphy2
import codecs
from settings import config
from preprocess.preprocess import stem_snowball

def get_all_forms(word):
    """Полный разбор слова"""
    morph = pymorphy2.MorphAnalyzer()
    output = set()
    for i in morph.parse(word):
        for j in i.lexeme:
            output.add(j.word)
    return output

def expand_words(path_in, path_out):

    path_in = "{0}/Thesis/senti/dict/{1}/EmotionLookupTable.txt".format(config.get("home_path"), path_in)
    path_out = "{0}/Thesis/senti/dict/{1}/EmotionLookupTable.txt".format(config.get("home_path"), path_out)

    morph = pymorphy2.MorphAnalyzer()

    with open(path_in, "r") as infile, open(path_out, 'w') as outfile:
        #Очищаем файл
        outfile.truncate()

        for num, line in enumerate(infile):
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            nline = line
            if nline.startswith(codecs.BOM_UTF8):
                nline = nline[3:]
            nline = nline.strip()
            word = nline.split('\t')[0].strip().decode("utf8")
            score = int(nline.split('\t')[1])

            if "*" not in word:
                """ Берём слова """
                stemmed = stem_snowball(word)
                exclude_words = [u"зря"]

                if len(stemmed) < 4:
                    """Слишком короткие заменяем всеми словоформами"""
                    if word in exclude_words:
                        outfile.write(word.encode('utf-8') + "\t" + str(score).encode('utf-8') + "\n")
                    else:
                        for form in get_all_forms(word):
                            outfile.write(form.encode('utf-8') + "\t" + str(score).encode('utf-8') + "\n")

                if len(stemmed) >= 4:
                    """Для некоротких создаём правило на основе стемминга"""
                    if len(stemmed) < len(word):
                        """ Если стемминг имел место, заменяем усечённую часть * """
                        result_word = stemmed + "*"
                        outfile.write(result_word.encode('utf-8') + "\t" + str(score).encode('utf-8') + "\n")
                    else:
                        """ Иначе оставляем как было """
                        result_word = word  # == stemmed
                        outfile.write(result_word.encode('utf-8') + "\t" + str(score).encode('utf-8') + "\n")
            else:
                 outfile.write((word + "\t" + str(score) + "\n").encode('utf-8'))


def remove_duplicates(path):
    #TODO не обрабатывается ситуация с разными баллами у одного слова

    path = "{0}/Thesis/senti/dict/{1}/EmotionLookupTable.txt".format(config.get("home_path"), path)
    dict = []
    seen = set()
    output = []

    with open(path, 'r',) as dict_file:
        for num, line in enumerate(dict_file):
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0].strip().decode("utf8")
            score = int(line.split('\t')[1])
            dict.append((word, score))
            for item in dict:
                if item[0] not in seen:
                    output.append(item)
                    seen.add(item[0])

    with open(path, 'w') as dict_file:
        for item in output:
            dict_file.write((item[0] + "\t" + str(item[1]) + "\n").encode('utf-8'))


def merge_dicts(in_dicts_list, out_dict):
    result_dict = []
    for dict in in_dicts_list:
        path_in = "{0}/Thesis/senti/dict/{1}".format(config.get("home_path"), dict)
        path_out = "{0}/Thesis/senti/dict/{1}".format(config.get("home_path"), out_dict)

        with open(path_in, 'r',) as dict_file:
            for num, line in enumerate(dict_file):
                if line.startswith(codecs.BOM_UTF8):
                    line = line[3:]
                line = line.strip()
                print num, line
                word = line.split('\t')[0].strip().decode("utf8")
                score = int(line.split('\t')[1])
                result_dict.append((word, score))

    '''Удаляем дубликаты'''
    seen = set()
    output = []
    for item in result_dict:
        if item[0] not in seen:
            output.append(item)
            seen.add(item[0])
    output.sort(key=lambda tup: tup[0])

    with open(path_out, 'w') as dict_out_file:
        for item in output:
            dict_out_file.write((item[0] + "\t" + str(item[1]) + "\n").encode('utf-8'))

# merge_dicts(["ru_tmp/EmotionLookupTable.txt", "ru2_tmp/EmotionLookupTable.txt", "my.txt"], "result_dict.txt")

# java -jar /Users/olegnagornyy/Thesis/senti/SentiStrengthCom.jar sentidata /Users/olegnagornyy/Thesis/senti/dict/ru/ stdin noDictionary illegalDoubleLettersInWordMiddle ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded explain text сука+блять
