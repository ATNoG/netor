#!/bin/bash
# @Author: Rafael Direito
# @Date:   2022-10-24 19:30:46
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-24 19:32:03
cd keycloak/server/
docker build -t "jboss/keycloak:18.0.2" .
