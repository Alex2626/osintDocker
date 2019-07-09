#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sendMailZipOutlook
import configparser
import datetime
import os
import shutil

# Datos
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'conf/scriptGestionInformes.conf')
config.read(config_path)

# Paths
dir_ReportsOutputs = config.get('Paths', 'INFORMES_OUTPUTS')
dir_tools = config.get('Paths', 'TOOLS')
dir_utilInfoOutputs = config.get('Paths', 'UTILINFO_PATH')

tools = config.get('Tools', 'TOOLS_NAMES').split(", ")

# Date
dirName = datetime.date.today().strftime("%Y-%m-%d")
edate = dirName
sdate = (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime("%Y-%m-%d")

weekDirName = sdate + "-to-" + edate


def main():
    print('Ejecutando Gestion de informes...')

    createDir(dir_ReportsOutputs + weekDirName)
    getReports(tools)
    getReportUtilInfo()
    file_zip = compressDir(dir_ReportsOutputs + weekDirName)

    # sendMailZipOutlook.printer1()

    sendMailZipOutlook.sendMail(file_zip)


def printInformes():
    print('GEstion informes ejecutando.....')


def getReportUtilInfo():
    try:
        if not os.path.exists(dir_ReportsOutputs + weekDirName + '/UtilInfo/'):
            os.mkdir(dir_ReportsOutputs + weekDirName + '/UtilInfo/')

        shutil.copy(dir_utilInfoOutputs + 'UtilInfo-Dorks-' + edate + '.zip', dir_ReportsOutputs + weekDirName + '/UtilInfo/')
        shutil.copy(dir_utilInfoOutputs + 'UtilInfo-Shodan-' + edate + '.zip',
                    dir_ReportsOutputs + weekDirName + '/UtilInfo/')


    except shutil.Error as err:
        print('Error'.format(err))


def getReports(tools):
    # Informes de una semana
    for tool in tools:

        dir_InformesByTool = (dir_ReportsOutputs + weekDirName + '/' + tool)
        createDir(dir_InformesByTool)

        print(dir_InformesByTool)

        dir = (dir_tools + tool + "/Outputs/")
        os.chdir(dir)  # Glob1() No me interpretaba la ruta

        auxDate = datetime.date.today()

        while str(auxDate) > str(sdate):
            if os.path.isfile(tool + '-' + str(auxDate) + '.zip'):
                zip = tool + '-' + str(auxDate) + '.zip'
                print(tool + '-' + str(auxDate) + '.zip')
                try:
                    print('INFORME DENTRO DE LA SEMANA QUE CORRESPONDE')
                    shutil.copy(zip, dir_InformesByTool)

                except shutil.Error:
                    print('ERROR al copiar informes')
            auxDate = (auxDate - datetime.timedelta(days=1))


def createDir(name):
    try:
        os.mkdir(name)
    except OSError as err:
        print("El directorio ya existe, no hay que crearlo".format(err))


def compressDir(dirName):
    # Si no me lo genera fuera de Outputs
    os.chdir(dir_ReportsOutputs)
    file_zip = shutil.make_archive(weekDirName, "zip", base_dir=weekDirName)

    return file_zip


if __name__ == "__main__":
    main()
