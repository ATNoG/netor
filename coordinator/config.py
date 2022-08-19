# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-08-19 16:06:31
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-08-19 18:44:36
import os
POSTGRES_USER=os.getenv("POSTGRES_USER","postgres")
POSTGRES_PASS=os.getenv("POSTGRES_PASS","postgres")
POSTGRES_DB=os.getenv("POSTGRES_DB","vsLCM")
POSTGRES_IP=os.getenv("POSTGRES_IP","localhost")
POSTGRES_PORT=os.getenv("POSTGRES_PORT",5432)
APP_SECRET=os.getenv("APP_SECRET","tenantManager")
APP_PORT=os.getenv("APP_PORT",5000)
RABBIT_USER=os.getenv("RABBIT_USER","admin")
RABBIT_PASS=os.getenv("RABBIT_PASS","admin")
RABBIT_IP=os.getenv("RABBIT_IP","localhost")
RABBIT_PORT=os.getenv("RABBIT_PORT",5672)
IDP_IP=os.getenv("IDP_IP","localhost")
IDP_PORT=os.getenv("IDP_PORT",5002)
IDP_ENDPOINT=os.getenv("IDP_ENDPOINT","/validate")
ENVIRONMENT=os.getenv("ENVIRONMENT","testing")
CATALOGUE_IP=os.getenv("CATALOGUE_IP","localhost")
CATALOGUE_PORT=os.getenv("IDP_PORT",5010)
DOMAIN_IP=os.getenv('DOMAIN_IP',"localhost")
DOMAIN_PORT=os.getenv("IDP_PORT",5001)
DNS_API_BASE_ENDPOINT=os.getenv("DNS_API_BASE_ENDPOINT")
DNS_API_KEY=os.getenv("DNS_API_KEY")
