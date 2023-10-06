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
    project_id = request.form.get('project_id')
    #project = pdb.get_project(project_id)
    #project = jsanitize(project)
    task = processing.apply_async((project_id,))
    pdb.update_project_celery_id(project_id, task.id)
    return jsonify({'task_id': task.id}), 202


@task.route("/cancel", methods=['POST'])
def cancel():
    pdb = ProjectDatabase()
    project_id = request.form.get('project_id')
    data = pdb.get_celery_id(project_id)

    # Revoke the Celery task
    capp.control.revoke(data.get('celery_id'), terminate=True)

    # Update the project's status to 'canceled'
    pdb.update_project_status(project_id, "canceled")

    return jsonify({'message': 'Task canceled successfully!'}), 200
