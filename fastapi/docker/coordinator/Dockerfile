FROM python:3.8

 
COPY ./coordinator/API /app

ADD ./docker/coordinator/entrypoint.sh /app
ADD ./docker/utils/telegraf /usr/bin/
ADD ./docker/coordinator/telegraf.conf /app

WORKDIR /app

RUN apt-get update && \
    apt-get -y install netcat

RUN python3 -m pip install -r requirements.txt


RUN chmod +x /usr/bin/telegraf
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]