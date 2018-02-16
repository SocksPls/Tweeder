from pymongo import MongoClient

client = MongoClient()
db = client.tweeder
accounts_db = db.accounts

accounts_db.update_many({}, {
    '$push': {
        "verified": False,
        "following": []
    }
}, upsert=True)