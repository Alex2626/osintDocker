#!/usr/bin/python3
# -*- coding: utf-8 -*-
import configparser
import datetime
import os
import shutil

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'conf/scriptUtilInfo.conf')
config.read(config_path)

# Paths
pathOutputs = config.get('Paths', 'OUTPUTS_PATH')
basePath = config.get('Paths', 'BASE_PATH')
toolsPath = config.get('Paths', 'TOOLS_PATH')

# Data
tools = config.get('Tools', 'TOOLS_NAMES').split(', ')

# Date
dirName = datetime.date.today().strftime("%Y-%m-%d")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%Y-%m-%d")


def main():
    print('Util Info')
    compareFiles()
    compressDir()


def createDir(toolName):
    if os.path.exists(pathOutputs + toolName + '/' + edate):
        print ('SI Existe directorio')
    else:
        print('No existe el directorio')
        print('Creando directorio: ' + toolName)
        os.mkdir(pathOutputs + toolName + '/' + edate)


def compareFiles():
    for tool in tools:

        dirAux = toolsPath + tool + '/Outputs/' + edate + '/'
        dir = os.listdir(dirAux)
        if not os.path.exists(tool):
            createDir(tool)

        for file in dir:
            try:

                fileBase = basePath + tool + '/' + file
                fileToCompare = dirAux + file
                fileOutput = pathOutputs + tool + '/' + edate + '/' + file

                if os.path.exists(fileOutput):
                    os.remove(fileOutput)

                script = ('diff ' + fileBase + ' ' + fileToCompare + ' > ' + fileOutput)
                print(script)
                os.system(script)
            except OSError as err:
                print ('ERROR'.format(err))


def compressDir():
    # Si no me lo genera fuera de Outputs
    os.chdir(pathOutputs + 'Shodan')
    b_dir1 = pathOutputs + 'Shodan/' + edate

    if os.path.exists(pathOutputs + 'Shodan/' + 'UtilInfo-Shodan-' + edate + '.zip'):
        os.remove(pathOutputs + 'Shodan/' + 'UtilInfo-Shodan-' + edate + '.zip')

    shutil.make_archive('UtilInfo-Shodan-' + edate, 'zip', b_dir1)
    #shutil.make_archive(base_dir=b_dir1, root_dir=b_dir1, format='zip', base_name='UtilInfo-Shodan-' + edate)

    if os.path.exists(pathOutputs + 'UtilInfo-Shodan-' + edate + '.zip'):
        os.remove(pathOutputs + 'UtilInfo-Shodan-' + edate + '.zip')

    shutil.move(pathOutputs + 'Shodan/' + 'UtilInfo-Shodan-' + edate + '.zip', pathOutputs)

    os.chdir(pathOutputs + 'Dorks')
    b_dir2 = pathOutputs + 'Dorks/' + edate

    if os.path.exists(pathOutputs + 'Dorks/' + 'UtilInfo-Dorks-' + edate + '.zip'):
        os.remove(pathOutputs + 'Dorks/' + 'UtilInfo-Dorks-' + edate + '.zip')

    shutil.make_archive('UtilInfo-Dorks-' + edate, 'zip', b_dir2)
    #shutil.make_archive(base_dir=b_dir1, root_dir=b_dir2, format='zip', base_name='UtilInfo-Dorks-' + edate)

    if os.path.exists(pathOutputs + 'UtilInfo-Dorks-' + edate + '.zip'):
        os.remove(pathOutputs + 'UtilInfo-Dorks-' + edate + '.zip')

    shutil.move(pathOutputs + 'Dorks/' + 'UtilInfo-Dorks-' + edate + '.zip', pathOutputs)


if __name__ == "__main__":
    main()
