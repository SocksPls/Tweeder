from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
from gridfs.errors import NoFile

client = MongoClient()
db = client.tweeder
files_db = gridfs.GridFS(client.tweeder_files)
accounts_db = db.accounts


def get_file(oid):
    try:
        files_db.get(ObjectId(oid))
    except NoFile:
        return False

