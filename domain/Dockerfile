FROM ubuntu:20.04

COPY . .

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

RUN chmod +x installDrivers.sh
RUN ./installDrivers.sh

RUN pip3 install -r requirements.txt


CMD python3 main.py



# Install charm to be able to build OSM packages with charms
#sudo snap install charm --classic