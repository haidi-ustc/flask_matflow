from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from config import config
from task.celery import init_celery

def create_app(config_name):

    print(" * Creating Flask app...")   # Debugging print statement
    app = Flask('matflow')

    app.config.from_object(config[config_name])

    # Set up utilities on app
    app.mongo = PyMongo(app)
    app.jwt =  JWTManager(app)
    app.bcrypt = Bcrypt(app)

    regist_blueprints(app)
    #print(app.config)

    print(" * Creating Celery app...")   # Debugging print statement
    init_celery(app)
    #celery_app.conf.update(app.config)
    
    return app


def regist_blueprints(app):

    from api import api
    from main import main
    from task import task
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(task, url_prefix='/task')

