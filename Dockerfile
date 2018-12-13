FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip

RUN mkdir /src
COPY . /src

WORKDIR /src

RUN pip3 install -r requirements.txt

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

EXPOSE 80

RUN gunicorn --timeout 300 frontend.wsgi --log-file -

# CMD ["gunicorn", "server.py"]