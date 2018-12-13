FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip

RUN mkdir /src
COPY requirements.txt /src

WORKDIR /src

RUN pip3 install -r requirements.txt

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

EXPOSE 8000
COPY . /src
ENV PYTHONPATH /src
CMD ["gunicorn", "--timeout", "300", "frontend.wsgi", "--log-file", "-", "--bind", "0.0.0.0"]