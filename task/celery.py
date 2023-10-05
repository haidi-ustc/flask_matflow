#from flask import current_app as flask_app
from celery.utils.log import get_task_logger

from celery import Celery

# You might have different configurations for development and production.
# Here, we'll fetch the 'development' config, but in a real-world scenario,
# you'd probably want to determine which config to use based on environment variables or other methods.
#capp = Celery('matflow', broker=flask_app.config['CELERY_BROKER_URL'],
#                    backend = flask_app.config['CELERY_RESULT_BACKEND'],
#                    inclue = ["task.test"]
#                    )
logger = get_task_logger(__name__)
capp = Celery('matflow',broker="redis://localhost:6379/0",
              backend="redis://localhost:6379/0",
              inclue = ["task.test"],
              broker_connection_retry_on_startup=True)
def init_celery(app):

    capp.config_from_object(app.config)
    #print(capp)
    #capp.conf.update(flask_app.config)

#capp.conf.update(
#    CELERY_TASK_RESULT_EXPIRES=3600,
#    CELERY_MONGODB_BACKEND_SETTINGS = {
#    'database': 'matflow',
#    'taskmeta_collection': 'task'}
#    )
#

