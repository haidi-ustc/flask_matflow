from pymongo import MongoClient
import json
from bson import ObjectId
from datetime import datetime
mc=MongoClient("mongodb://user:123456@localhost:27037/matflow")
db=mc.get_database()
db.projects.drop()
proj2={"title":"test-2","description":"DFT is a test","created_time":datetime.now(),"ended_time":datetime.now(),'dag':{"name":'dft','code':'vasp'}}
proj1={"title":"test-1","description":"QE is a test","created_time":datetime.now(),"ended_time":datetime.now(),'dag':{"name":'dft','code':'QE'}}
db.projects.insert_one(proj2)
db.projects.insert_one(proj1)


