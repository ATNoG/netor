Install OSM Python Client's pre requirements:

```
# Ubuntu 18.04 pre-requirements
sudo apt-get install python3-pip libcurl4-openssl-dev libssl-dev
# CentOS pre-requirements
# sudo yum install python3-pip libcurl-devel gnutls-devel
sudo -H python3 -m pip install python-magic
# Install OSM Information model
sudo -H python3 -m pip install git+https://osm.etsi.org/gerrit/osm/IM --upgrade
# Install OSM client from the git repo.
# You can install the latest client from master branch in this way:
sudo -H python3 -m pip install git+https://osm.etsi.org/gerrit/osm/osmclient
```


Install requirements:
```
pip3 install -r requirements.txt
````
