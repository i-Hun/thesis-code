# -*- coding: utf-8 -*-
import shlex
import subprocess
import platform

if platform.system() == "Darwin":
    os_specific_path = "/Users/olegnagornyy"
else:
    os_specific_path = "/home/hun/"

print os_specific_path

class RateSentiment(object):
    def __init__(self, text):
        self.text = text

    def senti_tuple(self):
        #open a subprocess using shlex to get the command line string into the correct args list format
        # добавить параметр explain для объяснения вывода изменить на
        p = subprocess.Popen(shlex.split("java -jar {0}/Thesis/senti/SentiStrengthCom.jar stdin noDictionary illegalDoubleLettersInWordMiddle"
                                         " ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded sentidata "
                                         "{0}/Thesis/senti/dict/ru/".format(os_specific_path)),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #communicate via stdin the string to be rated. Note that all spaces are replaced with +
        stdout_text, stderr_text = p.communicate(self.text.replace(" ", "+"))
        #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
        stdout_text = stdout_text.rstrip().replace("\t","")
        if stderr_text:
            print("Ошибка в модуле оценки эмоций:" + stderr_text)
        senti_tuple = (int(stdout_text.split("-")[0]), -int(stdout_text.split("-")[1]))
        return senti_tuple

    def rate(self):
        return self.senti_tuple()[0] + self.senti_tuple()[1]

    def explain(self):
        p = subprocess.Popen(shlex.split("java -jar {0}/Thesis/senti/SentiStrengthCom.jar stdin noDictionary illegalDoubleLettersInWordMiddle"
                                         " ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded sentidata "
                                         "{0}/Thesis/senti/dict/ru/".format(os_specific_path)),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_text, stderr_text = p.communicate(self.text.replace(" ", "+"))
        stdout_text = stdout_text.rstrip().replace("\t","")
        if stderr_text:
            print("Ошибка в модуле оценки эмоций:" + stderr_text)
        return stdout_text


def tuple_from_dict():
    import codecs

    path1 = "~/Thesis/senti/dict/ru/EmotionLookupTable.txt"
    path2 = "~/Thesis/senti/dict/ru2/EmotionLookupTable.txt"
    path3 = "~/Thesis/senti/dict/ru3/EmotionLookupTable.txt"

    dict1 = []
    dict2 = []
    dict3 = []

    with open(path1) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict1.append((word, score))

    with open(path2) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict2.append((word, score))

    with open(path3) as f:
        for line in f:
            # http://en.wikipedia.org/wiki/Byte_order_mark#UTF-8
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            line = line.strip()
            word = line.split('\t')[0]
            score = int(line.split('\t')[1])
            dict3.append((word, score))

    return dict1 + dict2 + dict3