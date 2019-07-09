#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import shutil
import datetime
import os



# Data
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'conf/scriptShodan.conf')
config.read(config_path)

pathOutputs = config.get('Paths', 'OUTPUTS_PATH')

searchs = config.get('Data_Searchs', 'SEARCHS').split(", ")

dirName = datetime.date.today().strftime("%Y-%m-%d")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%Y-%m-%d")


def main():
    print('Ejecutando Shodan...')
    createDir(dirName)
    shodanExe(searchs)
    compressDir(dirName)

def printShodan():
    print('SHODAN EJECUTANDO------')


def createDir(name):
    if os.path.exists(pathOutputs + name):
        print ('SI Existe directorio')
    else:
        print('No existe el directorio')
        print('Creando directorio: ' + name)
        os.mkdir(pathOutputs + name)


def shodanExe(searchs):
    for search in searchs:
        name = (search.split()[len(search.split()) - 2])
        try:
            os.system('shodan ' + search + ' > ' + pathOutputs + dirName + '/' + name)

        except OSError as err:
            print("Error: el archivo ya existe, hay que borrar lo anterior".format(err))


def moveReportToDefaultDir(reportName):
    if os.path.exists(pathOutputs + dirName + '/' + reportName):
        try:
            print('EXISTE EL ARCHIVO')
            os.remove(pathOutputs + dirName + '/' + reportName)
            shutil.move(originalOutputsPath + reportName, pathOutputs + dirName)
        except OSError as err:
            print('Error: '.format(err))
    else:
        print('NO EXISTE EL ARCHIVO')
        try:
            shutil.move(originalOutputsPath + reportName, pathOutputs + dirName)
        except shutil.Error as err:
            print('Error: '.format(err))


def compressDir(dirName):
    # Si no me lo genera fuera de Outputs
    os.chdir(pathOutputs)
    shutil.make_archive("Shodan-" + dirName, "zip", base_dir=dirName)


if __name__ == "__main__":
    main()
