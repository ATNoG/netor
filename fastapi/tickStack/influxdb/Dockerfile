FROM influxdb:1.8

RUN apt-get update
# RUN apt-get install -y tar git curl nano vim wget net-tools build-essential

WORKDIR /influxdb

COPY setup.sh /docker-entrypoint-initdb.d/
