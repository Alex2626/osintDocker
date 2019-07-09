#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import threading
import configparser
import shutil
import time
import datetime
import getopt
import os
import smtplib
import sys

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'conf/scriptDorks.conf')
config.read(config_path)

pathOutputs = config.get('Paths', 'OUTPUTS_PATH')

dirName = datetime.date.today().strftime("%d-%m-%Y")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%d-%m-%Y")


def main():
    print('Abriendo links generados con Dorks...')
    readFileF(pathOutputs + '05-07-2018/google-URJCsearchs.txt')
    # openFiles(pathOutputs)


def readFileF(path):

    file = open(path, "r")
    for line in file.readlines():
        if re.search('$', line):
            print(line)

if __name__ == "__main__":
    main()
