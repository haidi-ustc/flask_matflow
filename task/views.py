from flask import jsonify
from flask_jwt_extended import jwt_required
from task.test import start_processing, my_celery_task
from task.celery import capp

from task import task

@task.route('/test/<arg1>/<arg2>')
def test(arg1, arg2):
    task = my_celery_task.delay(int(arg1), int(arg2))
    return jsonify({"message": "Task started", "task_id": task.id})

@task.route('/test1/')
def test1():
    task = start_processing.delay()
    return jsonify({"message": "Task started", "task_id": task.id})

#@jwt_required()
@task.route('/submit_task', methods=['POST','GET'])
def submit_task():
    task = start_processing.apply_async()
    return jsonify({'task_id': task.id}), 202

#@jwt_required()
@task.route('/check_task/<task_id>', methods=['GET'])
def check_task(task_id):
    task = start_processing.AsyncResult(task_id, app=capp)
    print(type(task.info), task.info)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 10,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info)
        }
    return jsonify(response)

#@jwt_required()
@task.route('/cancel_task/<task_id>', methods=['POST','GET'])
def cancel_task(task_id):
    task = start_processing.AsyncResult(task_id, app=capp)
    task.revoke(terminate=True)
    return jsonify({'status': 'Task Canceled'}), 202


