FROM debian:stretch-slim

MAINTAINER AlejandroSanchez 

ENV DEBIAN_FRONTEND noninteractive 

WORKDIR  /osint-auto

ADD . /osint-auto

RUN apt-get update ; apt-get install -y python python-pip build-essential chrpath libssl-dev libxft-dev python-openssl python-pyexiv2 python3 --no-install-recommends 

RUN apt-get install -y libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev wget

RUN pip install wheel
RUN pip install	shodan
RUN pip install tweepy
RUN pip install image
RUN pip install exifread
RUN pip install jinja2
RUN pip install oauth2



RUN shodan init lRZ7k0qgCsdShbjMuPwF8A74Vt0jOT4s

RUN shodan myip

ENTRYPOINT ["/bin/bash"]
