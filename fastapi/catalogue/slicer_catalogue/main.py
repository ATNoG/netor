# @Author: Daniel Gomes
# @Date:   2022-08-16 09:35:51
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 20:44:12
import os
import importlib
import inspect
import api.models
from flask import Flask
from api.views.__init__ import vs_descriptor
from api.views.__init__ import vs_blueprint
from api.settings import DevConfig, ProdConfig
from mongoengine import Document, DynamicDocument
from flask_mongoengine import MongoEngine
from rabbitmq.messaging import MessageReceiver
from api.auth import loginManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from oidc import oidc
import logging
APPLICATION_NAME = os.environ.get('APPLICATION_NAME', 'catalogues')


class ReverseProxied(object):
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.script_name
        return self.app(environ, start_response)


def init_flask():
    app = Flask(APPLICATION_NAME)
    env = os.getenv('ENVIRONMENT', 'dev')
    SWAGGER_URL = '/apidocs'
    API_URL = '/static/documentation.json'
    if env == 'prod':
        app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/catalogue')
        API_URL = '/catalogue/static/documentation.json'
    # API_URL = 'templates/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Catalogue API"
        }
    )
    CORS(app)

    # Configurations settings
    app.config.from_object(DevConfig)

    oidc.init_app(app)
    
    # Register flask's blueprints
    app.register_blueprint(vs_descriptor.app)
    app.register_blueprint(vs_blueprint.app)

    #Register SwaggerUI Blueprint
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    

    #  Connect database
    db = MongoEngine()
    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        # Create all collection before because of the multi document transcations
        database = db.get_db()
        for model in dir(api.models)[7:]:
            for name, cls in inspect.getmembers(importlib.import_module(f"api.models.{model}"), inspect.isclass):
                if 'api.models' in cls.__module__ and issubclass(cls, (Document, DynamicDocument)):
                    collection_name = cls.get_collection().name
                    if collection_name not in database.list_collection_names(filter={"name": collection_name}):
                        database.create_collection(collection_name)

    # Authentication
    loginManager.init_app(app)
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
    logging.getLogger('pika').propagate=False
    app.run(host="0.0.0.0", port=ProdConfig.PORT)


def init_rabbit():
    message_receiver = MessageReceiver()
    message_receiver.start()


if __name__ == '__main__':
    init_rabbit()
    init_flask()
