from flask import Flask, render_template, request, redirect, url_for, session, make_response, abort
from backend import accounts, timeline, files, messages

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
            if 'remember' in request.form.keys():
                session.permanent = True
            return redirect(url_for('profile'))
        else:
            return render_template('login.html',
                                   status=login_attempt['status'],
                                   message=login_attempt['message'])
    elif request.method == 'GET':
        if 'username' in session.keys():
            return redirect(url_for('logout'))
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
        if 'username' in session.keys():
            return redirect(url_for('logout'))
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
    return render_template('profile.html',
                           user=accounts.account_details(name),
                           logged_in=logged_in,
                           theme=accounts.get_theme(logged_in),
                           following=accounts.is_following(logged_in, name),
                           posts=posts)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.route('/newpost', methods=['POST'])
def new_post():
    username = session['username']
    timeline.post_status(username, request.form['status'])
    return redirect(request.referrer)


@app.route('/timeline', methods=['GET'])
def timeline_view():
    if 'username' in session.keys():
        logged_in = accounts.get_display_name(session['username'])
    else:
        return redirect(url_for('login'))
    posts = timeline.timeline_for_user(session['username'])
    return render_template('timeline.html',
                           logged_in=logged_in,
                           posts=posts,
                           theme=accounts.get_theme(logged_in))


@app.route('/global', methods=['GET'])
def global_timeline():
    if 'username' not in session.keys(): logged_in=False
    else: logged_in = accounts.get_display_name(session['username'])
    return render_template('global.html',
                           logged_in=logged_in,
                           posts=timeline.global_timeline(),
                           theme=accounts.get_theme(logged_in))


@app.route('/settings', methods=['GET', 'POST'])
def user_settings():
    if request.method == "GET":
        if 'username' in session.keys():
            logged_in = accounts.account_details(session['username'])['displayname']
            account = accounts.account_details(session['username'])
            return render_template('settings.html',
                                   logged_in=logged_in,
                                   account=account,
                                   theme=accounts.get_theme(session['username'].lower()))
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        print(request.files)
        print(request.form)
        if 'username' not in session.keys():
            return redirect(url_for('login'))
        updated_profile = {
            'bio': request.form['bio'],
            'gender': request.form['gender'],
            'location': request.form['location']
        }
        if 'profile_pic' in request.files.keys():
            profile_pic = files.upload_file(request.files['profile_pic'])
            updated_profile['profile_pic'] = profile_pic
        else:
            if accounts.account_details(session['username'].lower())['profile']['profile_pic']:
                profile_pic = accounts.account_details(session['username'].lower())['profile']['profile_pic']
                updated_profile['profile_pic'] = profile_pic
        accounts.set_theme(session['username'].lower(), request.form['theme'])
        username = session['username']
        accounts.update_profile(username, updated_profile)
        return redirect(request.referrer)


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
        return render_template('reply.html',
                               logged_in=logged_in,
                               posts=timeline.get_full_replies(post_id)[:-1],
                               reply_to=timeline.post_details(post_id),
                               theme=accounts.get_theme(logged_in))
    elif request.method == "POST":
        timeline.post_status(logged_in, request.form['status'], replyTo=post_id)
        return redirect(url_for('profile'))


@app.route("/follow/<user>", methods=["GET", "POST"])
def follow(user):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username']
    if request.method == "POST":
        accounts.follow(logged_in, user)
        return redirect(str("/profile/" + user))
    else:
        pass


@app.route("/unfollow/<user>", methods=["GET", "POST"])
def unfollow(user):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username']
    if request.method == "POST":
        accounts.unfollow(logged_in, user)
        return redirect(str("/profile/" + user))
    else:
        pass


@app.route("/view/<post_id>", methods=["GET"])
def view_thread(post_id):
    logged_in = session['username'] if ('username' in session.keys()) else False
    posts = timeline.get_full_replies(post_id)
    return render_template('view.html',
                           logged_in=logged_in,
                           posts=posts)


@app.route("/like/<post_id>", methods=["GET", "POST"])
def like_post(post_id):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username']
    if request.method == "POST":
        timeline.like_post(post_id, logged_in)
        return redirect(request.referrer)
    elif request.method == "GET":
        pass


@app.route("/unlike/<post_id>", methods=["GET", "POST"])
def unlike_post(post_id):
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username']
    if request.method == "POST":
        timeline.unlike_post(post_id, logged_in)
        return redirect(request.referrer)
    elif request.method == "GET":
        pass


@app.route("/files/<oid>", methods=['GET'])
def get_file(oid):
    fl = files.get_file(oid)
    if not fl: return abort(404)
    response = make_response(fl.read())
    response.mimetype = fl.content_type
    return response


@app.route("/mentions", methods=["GET"])
def mentions():
    if 'username' not in session.keys(): return redirect(url_for('login'))
    logged_in = session['username'].lower()
    return render_template("mentions.html",
                           logged_in=logged_in,
                           theme=accounts.get_theme(session['username'].lower()),
                           posts=timeline.get_mentions(logged_in))


@app.route("/messages", methods=["GET", "POST"])
def messages_blank():
    logged_in = session['username'] if ('username' in session.keys()) else False
    if 'username' not in session: return redirect(url_for('login'))
    if request.method == "GET":
        return render_template('messages.html', logged_in=logged_in)
    elif request.method == "POST":
        return redirect('/messages/'+request.form['messageuser'])


@app.route("/messages/<user>", methods=["GET", "POST"])
def messaging(user):
    logged_in = session['username'] if ('username' in session.keys()) else False
    if 'username' not in session: return redirect(url_for('login'))
    if request.method == "GET":
        return render_template(
            "messages.html",
            messaging=accounts.get_display_name(user),
            messages=messages.get_messages(logged_in, user.lower())
        )
    elif request.method == "POST":
        messages.send_message(
            accounts.get_display_name(logged_in),
            accounts.get_display_name(user),
            request.form['message_content']
        )


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True)
