FROM python:3.8

WORKDIR /app
 
COPY ./placement/API /app
ADD ./docker/utils/telegraf   /usr/bin/
ADD ./docker/placement/telegraf.conf /app
ADD ./docker/placement/entrypoint.sh /app

RUN apt-get update && \
    apt-get -y install netcat


RUN python3 -m pip install -r requirements.txt


RUN chmod +x /usr/bin/telegraf
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]