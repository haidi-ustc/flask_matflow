from flask import Blueprint

task = Blueprint('task', __name__)

from task import views
from utils.utils import get_logger

