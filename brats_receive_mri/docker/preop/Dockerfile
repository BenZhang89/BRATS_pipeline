FROM python:3.7

RUN apt-get update && apt-get install -y vim
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app

RUN pip install -r /app/requirements.txt
CMD /app/start.sh

