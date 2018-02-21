import pymongo, datetime
from bson.objectid import ObjectId

client = pymongo.MongoClient()
db = client.tweeder
accounts_db = db.accounts
timeline_db = db.statuses


def post_status(username, content, private=False, replyTo=False, location=False):
    currentTimeDate = datetime.datetime.now()
    account_object = accounts_db.find_one({'username': username.lower()})
    accounts_mentioned = []
    for word in content:
        if word.startswith("@"):
            if accounts_db.find({'username': username.lower()}).count() > 0:
                accounts_mentioned.append(word[1:])

    status = {
        'isRepost': False,
        'poster': account_object['displayname'],
        'posterid': account_object['_id'],
        'content': content.replace('\n', ' ').replace('\r', ''),
        'timePosted': currentTimeDate,
        'likes': [],
        'reposts': [],
        'replies': [],
        'replyTo': ObjectId(replyTo) if replyTo else False,
        'hashtags': [x for x in content.split() if x.startswith("#")],
        'location': False or location,
        'private': False or private,

    }

    timeline_db.insert_one(status)


def user_posts_by_username(username):
    return timeline_db.find({'posterid': accounts_db.find_one({"username": username})['_id']}).sort('timePosted', pymongo.DESCENDING)


def user_posts(account_object):
    return timeline_db.find({"posterid": account_object}).sort('timePosted', pymongo.DESCENDING)


def timeline_for_user(username):
    return timeline_db.find({'posterid':
                                 {'$in': accounts_db.find_one({'username': username})['following']}
                             }).sort('timePosted', pymongo.DESCENDING)


def global_timeline():
    return timeline_db.find({}).sort('timePosted', pymongo.DESCENDING)


def post_details(post_id):
    return timeline_db.find_one({"_id": ObjectId(post_id)})


def delete_post(post_id):
    timeline_db.update_one({"_id": ObjectId(post_id)},
                           {'$set': {'hidden': True}})


def get_parent(post_id):
    if timeline_db.find_one({"_id": timeline_db.find_one({"_id": ObjectId(post_id)})['replyTo']}):
        return timeline_db.find_one({"_id": timeline_db.find_one({"_id": ObjectId(post_id)})['replyTo']})
    else:
        return False
