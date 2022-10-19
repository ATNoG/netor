FROM python:3.8

WORKDIR /app
 
COPY ./tenant/API /app
ADD ./docker/utils/telegraf   /usr/bin/
ADD ./docker/tenant/telegraf.conf /app
ADD ./docker/tenant/entrypoint.sh /app

RUN apt-get update && \
    apt-get -y install netcat

RUN python3 -m pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh
RUN chmod +x /usr/bin/telegraf
ENTRYPOINT ["./entrypoint.sh"]