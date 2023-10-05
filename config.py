import os

class Config(object):
    NAME = 'matflow'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard_to_guess_string'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another_hard_to_guess_string'

    # Celery configurations
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TASK_RESULT_EXPIRES = 3600
    CELERY_MONGODB_BACKEND_SETTINGS = {
        'database': 'matflow',
        'taskmeta_collection': 'task'
    }
    ROOT_PATH="workspace"

class ServerConfig(Config):
    DEBUG = True
    MONGO_URI = os.environ.get('DEVELOPMENT_MONGO_URI') or  'mongodb://user:123456@localhost:27037/matflow'

class LaptopConfig(Config):
    DEBUG = True
    MONGO_URI = os.environ.get('DEVELOPMENT_MONGO_URI') or  'mongodb://haidi:123456@localhost:27017/matflow'

class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = os.environ.get('PRODUCTION_MONGO_URI') or 'mongodb://localhost:27017/proddatabase'

config = {
    'laptop': LaptopConfig,
    'server': ServerConfig,
    'production': ProductionConfig,
}

