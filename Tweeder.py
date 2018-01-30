from flask import Flask, render_template, request, redirect, url_for, session
from backend import accounts

app = Flask(__name__)
app.secret_key = "eVZ4EmVK70iETb03KqDAXV5sBHb3T73t"


@app.route('/')
def index():
    if 'username' in session.keys():
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login_attempt = accounts.login(username, password)
        if login_attempt['status'] == 'success':
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('login.html',
                                   status=login_attempt['status'],
                                   message=login_attempt['message'])
    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password == confirm_password:
            register_attempt = accounts.create_account(email, username, password)
            return render_template('register.html',
                                   status=register_attempt['status'],
                                   message=register_attempt['message'])
        else:
            return render_template("register.html",
                                   status="danger",
                                   message="Passwords do not match!")
    elif request.method == 'GET':
        return render_template('register.html')


@app.route('/profile', methods=['GET'])
@app.route('/profile/<name>', methods=['GET'])
def profile(name=None):

    logged_in = True if ('username' in session.keys()) else False
    if not logged_in and name is None:
        return redirect(url_for('index'))
    if logged_in and name is None:
        name = session['username']
    name = name.lower()
    logged_in = 'username' in session.keys()
    dname = accounts.get_display_name(name)
    return render_template('profile.html', user=accounts.account_details(name), logged_in=logged_in)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.route('/layout')
def layout():
    return render_template('layout.html', logged_in=True)


if __name__ == '__main__':
    app.run(debug=True)
