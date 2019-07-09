#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
from Shodan import scriptShodan
from Tinfoleak import scriptTinfoleak
from Dorks import scriptDorks
from UtilInfo import scriptUtilInfo
from Informes import gestionInformes


def main():
    scriptShodan.printShodan()
    scriptTinfoleak.printTinfoleak()
    scriptDorks.printDorks()

    threads()

    scriptUtilInfo.main()
    gestionInformes.main()


def threads():
    thTinfoleak = threading.Thread(name='thTinfoleak',
                                   target=scriptTinfoleak.main,
                                   daemon=True)

    thDorks = threading.Thread(name='thDorks',
                               target=scriptDorks.main,
                               daemon=True)

    thShodan = threading.Thread(name='thShodan',
                                target=scriptShodan.main,
                                daemon=True)

    thTinfoleak.start()
    thDorks.start()
    thShodan.start()

    thTinfoleak.join()
    thDorks.join()
    thShodan.join()


if __name__ == "__main__":
    main()
