# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 13:40:58
# @Description: Contains several functions that should be invoked on startup

# custom imports
import aux.constants as Constants

# generic imports
import configparser
import logging
import os
import inspect

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
        Constants.DB_LOCATION = config['DB']['Location']
        Constants.DB_NAME = config['DB']['Name']
        Constants.DB_USER = config['DB']['User']
        Constants.DB_PASSWORD = config['DB']['Password']
        Constants.RABBITMQ_IP = config['RabbitMQ']['IP']
        Constants.RABBITMQ_PORT = config['RabbitMQ']['Port']
        Constants.RABBITMQ_USER = config['RabbitMQ']['User']
        Constants.RABBITMQ_PASS = config['RabbitMQ']['Password']
        Constants.REDIS_IP = config['Redis']['IP']
        Constants.REDIS_PORT = config['Redis']['Port']
        Constants.REDIS_USER = config['Redis']['User']
        Constants.REDIS_PASS = config['Redis']['Password']
    except Exception:
        return False, """The config file should have the folling sections with
                         the following variables:
                         DB -> Location, Name, User, Password"""
    return True, ""


def fill_database(db):
    pass