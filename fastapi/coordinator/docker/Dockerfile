FROM python:3.8

WORKDIR /app
 
COPY ./API /app
 
RUN apt-get update && \
    apt-get -y install netcat

RUN python3 -m pip install -r requirements.txt

COPY ./docker/entrypoint.sh /app
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]