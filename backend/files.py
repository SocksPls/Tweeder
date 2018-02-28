from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs.errors import NoFile
from werkzeug.utils import secure_filename
import gridfs

client = MongoClient()
db = client.tweeder
files_db = gridfs.GridFS(client.tweeder_files)
accounts_db = db.accounts


def get_file(oid):
    try:
        return files_db.get(ObjectId(oid))
    except NoFile:
        return False


def upload_file(file_to_upload):
    filename = secure_filename(file_to_upload.filename)
    obj = files_db.put(file_to_upload, content_type=file_to_upload.content_type, filename=filename)
    return obj
