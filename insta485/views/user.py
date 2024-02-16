"""
Insta485 users view.

URLs include:
GET /users/<user_url_slug>/
POST /following/?target=URL
POST /accounts/logout/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def show_user(user_url_slug):
    """Display user profile."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session.get('username')
    # Check if user exists
    cur = connection.execute(
        "SELECT * FROM users WHERE username = ?", (user_url_slug,)
    )
    user = cur.fetchone()
    if not user:
        flask.abort(404)

    # Get user's posts
    cur = connection.execute(
        "SELECT * FROM posts WHERE owner = ? "
        "ORDER BY created DESC, postid DESC",
        (user_url_slug,)
    )

    posts = cur.fetchall()

    total_posts = len(posts)
    cur = connection.execute(
        "SELECT COUNT(*) as follower_count FROM following WHERE username2 = ?",
        (user_url_slug,)
    )
    follower_count = cur.fetchone()['follower_count']
    cur = connection.execute(
        "SELECT COUNT(*) as following_count "
        "FROM following WHERE username1 = ?",
        (user_url_slug,)
    )
    following_count = cur.fetchone()['following_count']

    # Check if logname follows username
    if logname:
        cur = connection.execute(
            "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
            (logname, user_url_slug)
        )
        logname_follows_username = cur.fetchone() is not None
    else:
        logname_follows_username = False

    # Add database info to context
    context = {
        "logname": logname,
        "username": user_url_slug,
        "fullname": user['fullname'],
        "posts": posts,
        "total_posts": total_posts,
        "followers": follower_count,
        "following": following_count,
        "logname_follows_username": logname_follows_username
    }
    return flask.render_template("user.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def follow_unfollow_user():
    """Follow or unfollow a user."""
    target_url = flask.request.args.get('target', '/')
    operation = flask.request.form.get('operation')
    username = flask.request.form.get('username')
    logname = flask.session.get('username')

    if not username or not operation:
        flask.abort(400)  # Bad request

    connection = insta485.model.get_db()

    # Check if logname already follows/unfollows username
    cur = connection.execute(
        "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    already_follows = cur.fetchone() is not None

    if operation == 'follow':
        if already_follows:
            flask.abort(409)  # Conflict
        connection.execute(
            "INSERT INTO following (username1, username2) VALUES (?, ?)",
            (logname, username)
        )
    elif operation == 'unfollow':
        if not already_follows:
            flask.abort(409)  # Conflict
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username)
        )
    else:
        flask.abort(400)  # Bad request

    return flask.redirect(target_url)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Log the user out."""
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))
