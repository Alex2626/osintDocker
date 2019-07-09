#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
pathAppJs = config.get('Paths', 'APP_PATH')
dorksFile = config.get('Paths', 'DORKS_FILE')

# Data
engines = config.get('Data_Dorks', 'ENGINES').split(", ")
sites = config.get('Data_Dorks', 'SITES').split(", ")


dirName = datetime.date.today().strftime("%Y-%m-%d")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%Y-%m-%d")


def main():
    print('Ejecutando Dorks...')

    dir2 = createDir(dirName)

    threads(dir2, sites)
    compressDir(dirName)


def printDorks():
    print('Ejecutando Dorks....')


def createDir(name):
    if os.path.exists(pathOutputs + name):
        print ('SI Existe directorio')
    else:
        print('No existe el directorio')
        print('Creando directorio: ' + name)
        os.mkdir(pathOutputs + name)

    dir = pathOutputs + name
    return dir


def getSearchs(dirOutput, site):
    query = (
            #"phantomjs dorks.js google -D "+dorksFile +" -s "+site+" > " + dirOutput + "/" + site + "-searchs.txt")
            "phantomjs dorks.js google -D /root/Tools/PythonScripts/Dorks/conf/CONSULTAS2.txt -s marca.com")
    os.chdir(pathAppJs)
    os.system(query)


def threadTime():
    print('Ejecutando.... ' + threading.current_thread().getName())
    time.sleep(40)
    print('Finalizando.... ' + threading.current_thread().getName())


def threads(dirOutputs, sites):
    for site in sites:
        thSearchs = threading.Thread(name='th%s' % site,
                                     target=getSearchs,
                                     args=(dirOutputs, site,),
                                     daemon=True)
        thSearchs.start()

    thTime = threading.Thread(name='thTime%s' % site,
                              target=threadTime,
                              daemon=True)

    thPpal = threading.main_thread()

    thTime.start()
    thTime.join()


def compressDir(dirName):
    # Si no me lo genera fuera de Outputs
    os.chdir(pathOutputs)
    file_zip = shutil.make_archive("Dorks-" + edate, "zip", base_dir=dirName)


if __name__ == "__main__":
    main()
