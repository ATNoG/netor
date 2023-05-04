# @Author: Daniel Gomes
# @Date:   2022-08-16 09:35:51
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 20:35:27
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY',
                                'wz3DefHxgQTElMvACRAs1KgAUDPHgTqq')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    CACHE_TYPE = 'simple'
    PORT = 5010
    MONGODB_SETTINGS = {
        'username': os.environ.get('MONGO_USERNAME', 'catalogues'),
        'password': os.environ.get('MONGO_PASSWORD', 'catalogues'),
        'host': os.environ.get('MONGO_URL', 'localhost'),
        'port': 27017,
        'db': os.environ.get('MONGO_DB', 'catalogues')
    }
    OIDC_CLIENT_SECRETS = "./api/client_secrets.json"
    OIDC_OPENID_REALM = 'netor'


class AuthConfig:
    IDP_IP = os.getenv("IDP_IP", "localhost")
    IDP_PORT = os.getenv("IDP_PORT", 8001)
    IDP_ENDPOINT = os.getenv("IDP_ENDPOINT", "/oauth/validate/")


class ProdConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'prod'


class DevConfig(Config):
    """Development configurations"""
    DEBUG = True
    ENV = 'dev'
