from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from config import config
from celery import Celery

config_name = 'docker'
config = config[config_name]
print(" * Creating Celery app...")   # Debugging print statement
capp = Celery(config.NAME,broker=config.CELERY_BROKER_URL,
              backend=config.CELERY_RESULT_BACKEND,
              include = ["task.tasks"],
              broker_connection_retry_on_startup=True,
              ROOT_PATH=config.ROOT_PATH)

def create_app_mongo():
    print(" * Creating Flask-Mongo app...")   # Debugging print statement
    app = Flask(config.NAME)
    app.config.from_object(config)
    app.mongo = PyMongo(app)
    return app

def create_app():

    print(" * Creating Flask app...")   # Debugging print statement
    app = Flask(config.NAME)

    app.config.from_object(config)

    # Set up utilities on app
    app.mongo = PyMongo(app)
    app.jwt =  JWTManager(app)
    app.bcrypt = Bcrypt(app)

    regist_blueprints(app)

    
    return app

def regist_blueprints(app):

    from api import api
    from main import main
    from task import task
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(task, url_prefix='/task')

