"""
Insta485 following view.

URLs include:
GET /users/<user_url_slug>/following/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/following/', methods=['GET'])
def show_following(user_url_slug):
    """Display following of a user."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Check if user exists
    cur = connection.execute(
        "SELECT * FROM users WHERE username = ?", (user_url_slug,)
    ).fetchone()
    if not cur:
        flask.abort(404)

    logname = flask.session.get('username')
    # Query for following
    query = (
        "SELECT u.username, u.filename as user_img_url, "
        "(SELECT COUNT(*) FROM following "
        "WHERE username1 = ? AND username2 = u.username) "
        "as logname_follows_username "
        "FROM following f "
        "JOIN users u ON f.username2 = u.username "
        "WHERE f.username1 = ?"
    )
    following = connection.execute(query, (logname, user_url_slug)).fetchall()

    context = {
        "logname": logname,
        "username": user_url_slug,
        "following": following
    }
    return flask.render_template("following.html", **context)
