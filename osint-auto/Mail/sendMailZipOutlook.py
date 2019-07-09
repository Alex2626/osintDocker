#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Enviar correo Gmail con Python
import configparser
import getopt
import os
import smtplib
import sys

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Datos
config = configparser.ConfigParser()  # type: ConfigParser
config_path = os.path.join(os.path.dirname(__file__), 'sendMailOutlook.conf')
config.read(config_path)

username = config.get('Mail_Auth', 'LOGIN_USERNAME')
password = config.get('Mail_Auth', 'LOGIN_PASSWORD')

toaddrs = config.get('Mail_Addrs', 'TO_ADDRS')
fromaddr = config.get('Mail_Addrs', 'FROM_ADDRS')

messageHtml = config.get('Mail_Content', 'MESSAGE_HTML')


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o", ["ifile=", "app="])
    except getopt.GetoptError:
        print ('ERROR')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('Comando de ayuda')
            print ('sendMail.py -i <inputfile> ')
            print('--app NAME app que envía el correo')
        elif opt in ("-i", "--ifile"):
            print('sendMail...')

            inputfile = arg
            print(toaddrs.split(","))
            sendMail(inputfile)


def printer1():
    print('ESTAS EN SENDMAILZIPOUTLOOK SUBCARPETA')


def sendMail(file):
    # Load the email directions to send the email

    # Modificación del nombre para que no envie la ruta completa del archivo
    filename = file.split('/')[-1]

    subject = 'Informes: %s' % filename

    # Creating email
    header = MIMEMultipart()

    header['Subject'] = subject
    header['To'] = toaddrs
    header['From'] = fromaddr
    header.attach(MIMEText(messageHtml, 'html'))

    zip = getZipFile(file, filename)
    header.attach(zip)

    # Sending email
    print ('Cargando fichero...')
    print ('sending...')
    server = smtplib.SMTP('smtp.office365.com:587')

    server.starttls()

    server.login(username, password)
    server.sendmail(header['From'], header['To'].split(","), header.as_string())
    print ('Succesfully sent email...')
    server.quit()


def getZipFile(file, filename):
    fp = open(file, 'rb')
    zip2 = MIMEBase('application', 'zip')
    zip2.set_payload(fp.read())
    zip2.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    fp.close()
    encoders.encode_base64(zip2)
    return zip2


if __name__ == "__main__":
    main(sys.argv[1:])
