from flask import Flask, render_template, request, redirect, url_for, session
from backend import accounts, timeline

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
            session['username'] = username.lower() if "@" not in username else accounts.username_for_email(username)
            if request.form['remember']:
                session.permanent = True
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

    logged_in = session['username'] if ('username' in session.keys()) else False
    if not logged_in and name is None:
        return redirect(url_for('index'))
    if logged_in and name is None:
        name = session['username']
    name = name.lower()
    logged_in = accounts.get_display_name(session['username']) if 'username' in session.keys() else False
    posts = list(timeline.user_posts_by_username(name))
    return render_template('profile.html', user=accounts.account_details(name), logged_in=logged_in, posts=posts)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.route('/newpost', methods=['POST'])
def new_post():
    username = session['username']
    timeline.post_status(username, request.form['status'])
    return redirect(url_for('profile'))


@app.route('/timeline', methods=['GET'])
def timeline_view():
    if 'username' in session.keys():
        logged_in = accounts.get_display_name(session['username'])
    else:
        return redirect(url_for('login'))
    posts = timeline.timeline_for_user(session['username'])
    return render_template('timeline.html', logged_in=logged_in, posts=posts)


@app.route('/global', methods=['GET'])
def global_timeline():
    logged_in = True if 'username' in session.keys() else False
    return render_template('global.html', logged_in=logged_in, posts=timeline.global_timeline())


@app.route('/settings', methods=['GET', 'POST'])
def user_settings():
    if request.method == "GET":
        if 'username' in session.keys():
            logged_in = True
            profile = accounts.get_profile(session['username'])
            return render_template('settings.html', logged_in=logged_in, profile=profile)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        if 'username' not in session.keys():
            return redirect(url_for('login'))
        profile = {
            'bio': request.form['bio'],
            'gender': request.form['gender'],
            'location': request.form['location']
        }
        username = session['username']
        accounts.update_profile(username, profile)
        return redirect(url_for('profile'))


@app.route("/delete/<post_id>", methods=['GET'])
def delete_post(post_id):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    if session['username'] == timeline.post_details(post_id)['poster'].lower():
        timeline.delete_post(post_id)
        return redirect(url_for('profile'))
    else:
        return "No", 403


@app.route("/reply/<post_id>", methods=['GET', "POST"])
def reply_to_post(post_id):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username'] if ('username' in session.keys()) else False
    if request.method == "GET":
        return render_template('reply.html', logged_in=logged_in, reply_to=timeline.post_details(post_id))
    elif request.method == "POST":
        timeline.post_status(logged_in, request.form['status'], replyTo=post_id)
        return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
