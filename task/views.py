from flask import jsonify,request, current_app
from flask_jwt_extended import jwt_required
from task.tasks import processing
from app import capp
from bson import ObjectId
from utils.utils import jsanitize

from model import ProjectDatabase
from task import task


#@jwt_required()
@task.route("/submit",methods=['POST'])
def submit():
    pdb=ProjectDatabase()
    project_id = ObjectId(request.form.get('project_id'))
    project = pdb.get_project(project_id)
    project = jsanitize(project)
    task = processing.apply_async((project,))
    return jsonify({'task_id': task.id}), 202

