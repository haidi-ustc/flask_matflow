import os
import subprocess
from bson import ObjectId
from datetime import datetime
import time
from utils.utils import get_logger,hash_text,create_path,ChangeDirectory
from monty.serialization import loadfn,dumpfn
from app import  capp, create_app_mongo

from model import ProjectDatabase

logger = get_logger(__name__)

def get_bash():
    return """#!/bin/bash

# Define the path to the job_status file
STATUS_FILE="job_status"

# Write the initial status to the file
echo "pending" > $STATUS_FILE

# Simulate some initialization delay
sleep 5

# Update the status to "running"
echo "running" > $STATUS_FILE

# Simulate the task running
sleep 20

# Update the status to "complete"
echo "complete" > $STATUS_FILE
"""
@capp.task
def test_task(arg1, arg2):
    return arg1 + arg2


@capp.task()
def processing(project, force_execution=True):

    pdb = ProjectDatabase()   

    project_id = ObjectId(project['_id'])
    
    # Update the project status to 'running' in the pdb
    pdb.update_project_status(project_id, "running")
    
    hash = hash_text(project['dag'])
    root_path =  capp.conf['ROOT_PATH']
    create_path(root_path)
    logger.info("ROOT_PATH: %s"%root_path)
    root_workpath = os.path.join(root_path, hash)
    if not os.path.isdir(root_workpath):
        create_path(root_workpath)
    logger.info("ROOT_WORKPATH: %s"%root_workpath)
    dumpfn(project, os.path.join(root_workpath, 'project.json'), indent=4)
    
    # Simulate running an external bash script or program
    with ChangeDirectory(root_workpath):
        STATUS_FILE = "job_status"

        # If force_execution is True, delete the job_status file if it exists
        if force_execution and os.path.exists("job_status"):
            os.remove(STATUS_FILE)

        with open('mytask.sh', 'w') as fid:
            fid.write(get_bash())
        os.chmod('mytask.sh', 0o755)
        process = subprocess.Popen(["./mytask.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   
        # Define the path to the job_status file

        # Wait for the job_status file to be created
        while not os.path.exists(STATUS_FILE):
            time.sleep(1)

        # Periodically check the status of the task
        while True:
            with open(STATUS_FILE, 'r') as file:
                status = file.read().strip()

            if status == "complete":
                print("Task completed!")
                # Update the project status to 'complete' in the pdb
                pdb.update_project_status(project_id, "complete")
                pdb.set_project_end_time( project_id, end_time=datetime.now())
                break
            elif status == "failure":
                print("Task is failed!")
                # Update the project status to 'failure' in the pdb
                pdb.update_project_status(project_id, "failure")
                pdb.set_project_end_time( project_id, end_time=datetime.now())
                break
            elif status == "running":
                pdb.update_project_status(project_id, "running")
                print("Task is running...")
            elif status == "pending":
                pdb.update_project_status(project_id, "pending")
                print("Task is pending...")

            time.sleep(5)  # Check every 5 seconds

