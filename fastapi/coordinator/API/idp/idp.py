# @Author: Daniel Gomes
# @Date:   2022-10-29 09:55:13
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 10:26:45
# custom imports
import aux.constants as Constants

# generic imports
import configparser
import logging
import os
import inspect
from fastapi_keycloak import FastAPIKeycloak
# Logger
logging.basicConfig(
    format="%(module)-15s:%(levelname)-10s| %(message)s",
    level=logging.INFO
)
currentdir = os.path.dirname(os.path.abspath(
             inspect.getfile(inspect.currentframe())))


def load_config():
    # load config
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Test config
    try:
        # Load Variables
        Constants.IDP_IP = config['IDP']['Ip']
        Constants.IDP_CLIENTID = config['IDP']['Client_ID']
        Constants.IDP_ClIENT_SECRET = config['IDP']['Client_Secret']
        Constants.IDP_ADMIN_ClIENTSECRET = config['IDP']['Admin_Client_Secret']
        Constants.IDP_REALM = config['IDP']['Realm']
        Constants.IDP_CALLBACK_URI = "http://localhost/8000/*"
    except Exception:
        return False, """The config file should have the IDP sectioN with
                         the following variables:"""
    return True, ""


load_config()
print(Constants.IDP_IP)
idp = FastAPIKeycloak(
    server_url=Constants.IDP_IP,
    client_id=Constants.IDP_CLIENTID,
    client_secret=Constants.IDP_ClIENT_SECRET,
    admin_client_secret=Constants.IDP_ADMIN_ClIENTSECRET,
    realm=Constants.IDP_REALM,
    callback_uri=Constants.IDP_CALLBACK_URI
)
