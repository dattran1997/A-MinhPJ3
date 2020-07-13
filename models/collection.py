from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps,loads

# mongodb+srv://admin:admin@cluster0-sbbfy.mongodb.net/test?retryWrites=true
# mongodb+srv://admin:admin@c4e27-cluster-v9wvw.mongodb.net/test?retryWrites=true
mongo_uri = "mongodb+srv://admin:admin@cluster0-sbbfy.mongodb.net/test?retryWrites=true"
client = MongoClient(mongo_uri)

freepix_database = client.db_freepix

User = freepix_database["User"]
Post = freepix_database['Post']
Admin = freepix_database['Admin']
Comments = freepix_database['Comments']
Albums = freepix_database['Albums']

# Admin.insert_one({
#     'username': 'admin',
#     'password': 'admin'
# })
