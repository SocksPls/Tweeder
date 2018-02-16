from pymongo import MongoClient
import bcrypt

client = MongoClient()
accounts_db = client.tweeder.accounts


def get_display_name(username):
    return accounts_db.find_one({'username': username})['displayname']


def is_verified(username):
    return accounts_db.find_one({'username': username})['verified']


def account_exists(username):
    return bool(accounts_db.find_one({'username': username}))


def account_details(username):
    return accounts_db.find_one({'username': username})


def validate_username(username):
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_"
    for char in username:
        if char not in allowed_chars:
            return False
    return True


def create_account(email, username, password):
    displayname = username
    username = username.lower()
    if not validate_username(username):
        return {
            'status': 'danger',
            'code': 6,
            'message': 'Username can only contain numbers, letters, and underscores'
        }

    if accounts_db.find_one({'username': username}):

        return {
            'status': 'danger',
            'code': 1,
            'message': 'Username already exists!'
        }

    elif accounts_db.find_one({'email': email}):

        return {
            'status': 'danger',
            'code': 2,
            'message': 'Email address already in use!'
        }

    elif email == "":
        return {
            'status': 'danger',
            'code': 3,
            'message': 'Email address cannot be blank!'
        }

    elif username == "":
        return {
            'status': 'danger',
            'code': 4,
            'message': "Username cannot be blank!"
        }

    elif password == "":
        return {
            'status': 'danger',
            'code': 5,
            'message': 'Password cannot be blank!'
        }

    else:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(14))
        accounts_db.insert_one({
            'username': username,
            'displayname': displayname,
            'email': email,
            'password': hashed_password,
            'verified': False,
            'following': [],
            'profile': {}
        })

        return {
            'status': 'success',
            'code': 0,
            'message': 'Account created!'
        }


def login(username, password):
    username = username.lower()

    # Check that account exists, either with username or email based login
    if accounts_db.find_one({'username': username}):
        account_document = accounts_db.find_one({'username': username})
    elif accounts_db.find_one({'email': username}):
        account_document = accounts_db.find_one({'email': username})
    else:

        return {
            'status': 'danger',
            'code': 1,
            'message': 'Account does not exist!'
        }

    # Do login stuff
    hashed_password = account_document['password']
    if hashed_password == bcrypt.hashpw(str.encode(password), hashed_password):

        return {
            'status': 'success',
            'code': 0,
            'message': 'Logged in!'
        }

    else:

        return {
            'status': 'danger',
            'code': 2,
            'message': 'Incorrect password'
        }


def follow(follower, following):
    following_doc = accounts_db.find_one({'username': following.lower()})
    following_id = following_doc['_id']

    accounts_db.update_one({'username': follower.lower()},
                           {'$push': {'following': following_id}})


def unfollow(follower, following):
    following_doc = accounts_db.find_one({'username': following.lower()})
    following_id = following_doc['_id']

    accounts_db.update_one({'username': follower.lower()},
                           {'$pull': {'following': following_id}})
