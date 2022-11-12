FROM python:3.8

WORKDIR /app
 
COPY ./test_manager/API /app
ADD ./docker/utils/telegraf   /usr/bin/
ADD ./docker/test_manager/telegraf.conf /app
ADD ./docker/test_manager/entrypoint.sh /app

RUN apt-get update && \
    apt-get -y install netcat


RUN python3 -m pip install -r requirements.txt


RUN chmod +x /usr/bin/telegraf
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]