from pymongo import MongoClient
# import json
import bcrypt

# try:
#     with open('config.json') as f:
#         config = json.loads(f.read())
# except FileNotFounddanger:
#     print("Config file does not exist!",
#           "Please copy and configure config.local.json to config.json in the root directory.")
#     exit()
# client = MongoClient(config['database'])


client = MongoClient()
accounts_db = client.tweeder.accounts


def create_account(email, username, password):

    displayname = username
    username = username.lower()

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
            'password': hashed_password
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
    