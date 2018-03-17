from pymongo import MongoClient
from bson.objectid import ObjectId
from backend import accounts

client = MongoClient()
db = client.tweeder
accounts_db = db.accounts
messages_db = db.messages


def send_message(msg_from, msg_to, msg_content):
    if type(msg_from) == str:
        from_id = accounts.get_profile(msg_from)['_id']
    elif type(msg_from) == ObjectId:
        from_id = msg_from

    if type(msg_to) == str:
        to_id = accounts.get_profile(msg_to)['_id']
    elif type(msg_to) == ObjectId:
        to_id = msg_to

    message = {
        'from': from_id,
        'to': to_id,
        'content': msg_content
    }

    messages_db.insert_one(message)