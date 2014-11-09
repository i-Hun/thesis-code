# -*- coding: utf-8 -*-
import shlex
import subprocess

def rate_sentiment(sentiString):
    #open a subprocess using shlex to get the command line string into the correct args list format
    p = subprocess.Popen(shlex.split("java -jar /home/hun/Thesis/sentistrength/ss.jar stdin noDictionary illegalDoubleLettersInWordMiddle ёйухцчщьыъ illegalDoubleLettersAtWordEnd абвгджзйкоуфхцчщэ UTF8 urlencoded sentidata /home/hun/Thesis/sentistrength/dict/rus/"), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #communicate via stdin the string to be rated. Note that all spaces are replaced with +
    stdout_text, stderr_text = p.communicate(sentiString.replace(" ","+"))
    #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
    stdout_text = stdout_text.rstrip().replace("\t","")
    if stderr_text:
        print("Ошибка в модуле оценки эмоций:" + stderr_text)
    return (int(stdout_text.split("-")[0]), -int(stdout_text.split("-")[1]))

# print rate_sentiment("Это был ужасный день, отвратительная погода")