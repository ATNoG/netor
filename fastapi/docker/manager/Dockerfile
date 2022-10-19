FROM python:3.8

 
COPY ./manager/API /app
ADD ./docker/utils/telegraf   /usr/bin/
ADD ./docker/manager/telegraf.conf /app
ADD ./docker/manager/entrypoint.sh /app

RUN apt-get update && \
    apt-get -y install netcat

WORKDIR /app

RUN python3 -m pip install -r requirements.txt


RUN chmod +x /usr/bin/telegraf
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]