#!/bin/bash
# @Author: Daniel Gomes
# @Date:   2022-08-16 09:35:51
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-28 14:55:52
#executed as sudo
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Clean the previous repos that might exist
sed -i "/osm-download.etsi.org/d" /etc/apt/sources.list

# Add OSM debian repo
curl -q -o OSM-ETSI-Release-key.gpg https://osm-download.etsi.org/repository/osm/debian/ReleaseTEN/OSM%20ETSI%20Release%20Key.gpg
apt-key add OSM-ETSI-Release-key.gpg
add-apt-repository -y "deb [arch=amd64] https://osm-download.etsi.org/repository/osm/debian/ReleaseTEN stable devops IM osmclient"
apt-get update

# Install OSM IM and osmclient packages from deb repo
apt-get install python3-osm-im python3-osmclient

# Install osmclient and osm_im dependencies via pip
python3 -m pip install -r /usr/lib/python3/dist-packages/osm_im/requirements.txt -r /usr/lib/python3/dist-packages/osmclient/requirements.txt
