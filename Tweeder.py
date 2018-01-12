from flask import Flask, render_template, request
from backend import accounts

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    login_attempt = accounts.login(username, password)
    return render_template('status.html',
                           title_status=login_attempt['status'].title(),
                           status=login_attempt['status'],
                           message=login_attempt['message'])


@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    if password == confirm_password:
        register_attempt = accounts.create_account(email, username, password)
        return register_attempt['message']
    else:
        return "Passwords do not match!"


if __name__ == '__main__':
    app.run(debug=True)
