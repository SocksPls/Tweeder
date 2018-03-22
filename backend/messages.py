from pymongo import MongoClient
from bson.objectid import ObjectId
from backend import accounts
import datetime

client = MongoClient()
db = client.tweeder
accounts_db = db.accounts
messages_db = db.messages


def send_message(msg_from, msg_to, msg_content):
    if type(msg_from) == str:
        from_id = accounts.get_profile(msg_from)['_id']
    elif type(msg_from) == ObjectId:
        from_id = msg_from
        msg_from = accounts_db.find_one({'_id': from_id})['displayname']

    if type(msg_to) == str:
        to_id = accounts.get_profile(msg_to)['_id']
    elif type(msg_to) == ObjectId:
        to_id = msg_to
        msg_to = accounts_db.find_one({'_id': to_id})['displayname']

    currentTimeDate = datetime.datetime.now()

    message = {
        'from': from_id,
        'to': to_id,
        'fromName': msg_from,
        'toName': msg_to,
        'content': msg_content,
        'timeSent': currentTimeDate
    }

    messages_db.insert_one(message)
