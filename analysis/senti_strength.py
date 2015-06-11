# -*- coding: utf-8 -*-
import shlex
import subprocess
import platform
from settings import config

class RateSentiment(object):
    def __init__(self, text):
        self.text = text

    def senti_tuple(self):
        #open a subprocess using shlex to get the command line string into the correct args list format
        # добавить параметр explain для объяснения вывода изменить на
        p = subprocess.Popen(shlex.split("java -jar {0}/Thesis/senti/SentiStrengthCom.jar stdin noDictionary illegalDoubleLettersInWordMiddle"
                                         " ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded sentidata "
                                         "{0}/Thesis/senti/dict/ru/".format(config.get("home_path"))),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #communicate via stdin the string to be rated. Note that all spaces are replaced with +
        stdout_text, stderr_text = p.communicate(self.text.replace(" ", "+"))
        #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
        stdout_text = stdout_text.rstrip().replace("\t","")
        if stderr_text:
            raise Exception("Ошибка в модуле оценки эмоций:" + stderr_text)
        senti_tuple = (int(stdout_text.split("-")[0]), -int(stdout_text.split("-")[1]))
        return senti_tuple

    def rate(self):
        return self.senti_tuple()[0] + self.senti_tuple()[1]

    def explain(self):
        p = subprocess.Popen(shlex.split("java -jar {0}/Thesis/senti/SentiStrengthCom.jar stdin noDictionary illegalDoubleLettersInWordMiddle"
                                         " ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded explain sentidata "
                                         "{0}/Thesis/senti/dict/ru/".format(config.get("home_path"))),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_text, stderr_text = p.communicate(self.text.replace(" ", "+"))
        print self.text.replace(" ", "+")
        if stderr_text:
            raise Exception("Ошибка в модуле оценки эмоций:" + stderr_text)
        return stdout_text
