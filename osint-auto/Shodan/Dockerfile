FROM python:4

RUN mkdir /shodan-auto
WORKDIR  /shodan-auto

COPỲ requirements.txt /shodan-auto

RUN pip install	-r requirements.txt

COPY . /shodan-auto

CMD ["python", "./scriptShodan.py"]
