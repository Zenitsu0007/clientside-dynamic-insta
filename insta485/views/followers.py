"""
Insta485 followers view.

URLs include:
GET /users/<user_url_slug>/followers/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/followers/', methods=['GET'])
def show_followers(user_url_slug):
    """Display followers of a user."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Check if user exists
    user = connection.execute(
        "SELECT * FROM users WHERE username = ?", (user_url_slug,)
    ).fetchone()
    if not user:
        flask.abort(404)

    logname = flask.session.get('username')
    # Query for followers
    query = (
        "SELECT u1.username, u1.filename as user_img_url, "
        "(SELECT COUNT(*) FROM following "
        "WHERE username1 = ? AND username2 = u1.username) "
        "as logname_follows_username FROM following f "
        "JOIN users u1 ON f.username1 = u1.username "
        "WHERE f.username2 = ?"
    )

    followers = connection.execute(query, (logname, user_url_slug)).fetchall()

    context = {
        "logname": logname,
        "username": user_url_slug,
        "followers": followers
    }
    return flask.render_template("followers.html", **context)
