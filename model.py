from app import create_app_mongo
from bson.objectid import ObjectId
from datetime import datetime

app = create_app_mongo()

class ProjectDatabase:
    def __init__(self):
        self.mongo = app.mongo 
        self.collection = self.mongo.db.projects

    def insert_project(self, title, description, dag={}):
        project = {
            "title": title,
            "description": description,
            "created_time": datetime.now(),
            "ended_time": None,  # Set to None during initialization
            "dag": dag,
            "status": "pending",
            "celery_id":None
        }
        result = self.collection.insert_one(project)
        return result.inserted_id

    def get_project(self, project_id):
        project_id = ObjectId(project_id)
        return self.collection.find_one({"_id": project_id})

    def get_celery_id(self, project_id):
        project_id = ObjectId(project_id)
        return self.collection.find_one({"_id": project_id},{"_id":0, "celery_id":1})

    def update_project_status(self, project_id, status):
        project_id = ObjectId(project_id)
        self.collection.update_one({"_id": project_id}, {"$set": {"status": status}})

    def update_project_celery_id(self, project_id, celery_id):
        project_id = ObjectId(project_id)
        self.collection.update_one({"_id": project_id}, {"$set": {"celery_id": celery_id}})

    def update_project_dag(self, project_id, dag_data):
        project_id = ObjectId(project_id)
        self.collection.update_one({"_id": project_id}, {"$set": {"dag": dag_data}})

    def get_project_dag(self, project_id):
        project_id = ObjectId(project_id)
        return self.collection.find_one({"_id": project_id},{"_id":0, "dag":1})

    def delete_project(self, project_id):
        project_id = ObjectId(project_id)
        self.collection.delete_one({"_id": project_id})

    def set_project_end_time(self, project_id, end_time=None):
        if end_time is None:
            end_time = datetime.now()
        project_id = ObjectId(project_id)
        self.collection.update_one({"_id": project_id}, {"$set": {"ended_time": end_time}})

# Usage example:
# db = ProjectDatabase()
# project_id = db.insert_project("test-1", "QE is a test")
# project = db.get_project(project_id)
# db.update_project_status(project_id, "running")

