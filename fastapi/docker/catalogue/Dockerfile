FROM python:3.9-slim

COPY ./catalogue/slicer_catalogue/ app

ADD ./docker/catalogue/entrypoint.sh /app
ADD ./docker/utils/telegraf /usr/bin/
ADD ./docker/catalogue/telegraf.conf /app

RUN apt update
RUN apt install -y build-essential && \ 
    apt-get -y install netcat

RUN python3 -m pip install --upgrade pip
WORKDIR  /app
RUN pip install -r requirements.txt
RUN chmod +x /usr/bin/telegraf
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]