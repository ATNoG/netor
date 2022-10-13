FROM ubuntu:20.04

WORKDIR /app

COPY ./API /app
COPY ./docker/installDrivers.sh /app

RUN apt-get update

RUN apt-get install -y libcurl4-openssl-dev=7.68.* \
    apt-utils=2.0.9 \
    libssl-dev=1.1.* \
    software-properties-common=0.99.9.* \
    apt-transport-https=2.0.9 \
    curl=7.68.*


RUN apt-get -y install \
    python3.8 \
    python3-setuptools=45.2.* \
    python3-dev=3.8.* \
    python3-pip=20.0.*

RUN apt-get update && \
    apt-get -y install netcat

RUN chmod +x installDrivers.sh
RUN ./installDrivers.sh


 
RUN python3 -m pip install -r requirements.txt

COPY ./docker/entrypoint.sh /app
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


# Install charm to be able to build OSM packages with charms
#sudo snap install charm --classic