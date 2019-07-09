#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import shutil
import threading
import time
import datetime
import getopt
import os
import smtplib
import sys

from timeit import default_timer as timer

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'conf/scriptTinfoleak.conf')
config.read(config_path)

# Paths
originalOutputsPath = config.get('Paths', 'ORIGINAL_OUTPUTS_PATH')
cssFile = config.get('Paths', 'CSS_PATH')
shPath = config.get('Paths', 'SH_PATH')
tinfoleakPath = config.get('Paths', 'APP_PATH')

pathOutputs = config.get('Paths', 'OUTPUTS_PATH')

dirName = datetime.date.today().strftime("%Y-%m-%d")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%Y-%m-%d")

users = config.get('Data_Searchs', 'USERS').split(", ")
nTweets = config.get('Data_Searchs', 'NTWEETS')
words = config.get('Data_Searchs', 'WORDS').split(", ")


def main():
    print('Ejecutando Tinfoleak...')

    createDir(dirName)
    # getReportsUsersURJC(users, edate, sdate)
    # getAdvancedSearch(words, edate, sdate)
    threads()
    compressDir(dirName)



def createDir(name):
    if os.path.exists(pathOutputs + name):
        print ('SI Existe directorio')
    else:
        print('No existe el directorio')
        print('Creando directorio: ' + name)
        os.mkdir(pathOutputs + name)

        # Copy Css file to the directory
        shutil.copy(cssFile, pathOutputs + name)


def getReportsUsersURJC():
    for user in users:
        print(user)
        print('----------')
        reportName = (user + '-' + dirName + '.html')
        commandUsersTinfoleak = (
                "./tinfoleak.py -u " + user + " -t " + nTweets + " -i --sdate " + sdate + " --edate " + edate + " --hashtags --mentions --find [+]urjc " + "-o " + reportName
        )

        print(commandUsersTinfoleak)
        os.chdir(tinfoleakPath)
        os.system(commandUsersTinfoleak)

        moveReportToDefaultDir(reportName)


def getAdvancedSearch():
    for word in words:
        reportName = ('S-' + word + '-' + dirName + '.html')
        commandAdSearchsTinfoleak = (
                "./tinfoleak.py -u urjc" + " -t " + nTweets + " -i --sdate " + sdate + " --edate " + edate + " --find [+]" + word + " --search -o " + reportName)

        os.chdir(tinfoleakPath)
        print(os.getcwd())
        os.system(commandAdSearchsTinfoleak)

        moveReportToDefaultDir(reportName)


def threads():
    for word in words:
        thAdvSearch = threading.Thread(name='thAdvSearch%s' % word,
                                       target=getAdvancedSearch,
                                       )
        thAdvSearch.start()

    for user in users:
        thReportUser = threading.Thread(name='thReportUser%s' % user,
                                        target=getReportsUsersURJC,
                                        )
        thReportUser.start()




def moveReportToDefaultDir(reportName):
    try:
        shutil.move(originalOutputsPath + reportName, pathOutputs + dirName)
    except OSError as err:
        print("Error: el archivo ya existe, hay que borrar lo anterior".format(err))
        print(pathOutputs + dirName + '/' + reportName)
        os.remove(pathOutputs + dirName + '/' + reportName)
        shutil.move(originalOutputsPath + reportName, pathOutputs + dirName)


def compressDir(dirName):
    # Si no me lo genera fuera de Outputs
    os.chdir(pathOutputs)
    shutil.make_archive("Tinfoleak-" + dirName, "zip", base_dir=dirName)


if __name__ == "__main__":
    main()
