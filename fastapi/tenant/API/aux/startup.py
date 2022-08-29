# @Author: Daniel Gomes
# @Date:   2022-08-16 09:40:42
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-27 11:53:28
# @Description: Contains several functions that should be invoked on startup

# custom imports
import aux.constants as Constants
from sql_app.crud import auth as CRUD_Auth

# generic imports
import configparser
import logging
import os
import inspect
import schemas.auth as AuthSchemas
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

    except Exception:
        return False, """The config file should have the folling sections with
                         the following variables:
                         DB -> Location, Name, User, Password"""
    return True, ""


def startup_roles(db):
    for role in Constants.USER_ROLES:
        CRUD_Auth.create_role(db, role)


def startup_groups(db):
    CRUD_Auth.create_group(db, "admin")
    CRUD_Auth.create_group(db, "user")


def create_default_admin(db):
    admin_tenant = AuthSchemas.TenantCreate(
        username=Constants.DEFAULT_ADMIN_CREDENTIALS['username'],
        password=Constants.DEFAULT_ADMIN_CREDENTIALS['password'],
        group="admin",
        roles=Constants.USER_ROLES
    )
    CRUD_Auth.register_tenant(db, admin_tenant)


def fill_database(db):
    startup_roles(db)
    startup_groups(db)
    create_default_admin(db)
