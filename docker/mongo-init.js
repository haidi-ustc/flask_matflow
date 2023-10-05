db = db.getSiblingDB("admin");
// move to the admin db - always created in Mongo
db.auth("admin", "admin");
// log as root admin if you decided to authenticate in your docker-compose file...
db = db.getSiblingDB("matflow");
// create and move to your new database
db.createUser({
'user': "user",
'pwd': "123456",
'roles': [{
    'role': "readWrite",
    'db': "matflow"}]});
// user created
db.createCollection("collection_test");

