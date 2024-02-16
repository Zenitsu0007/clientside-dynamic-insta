"""
Insta485 likes and unlikes.

URLs include:
/likes/?target=URL
"""
import flask
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def likes_unlike():
    """Like or Unlike a post."""
    target_url = flask.request.args.get('target', '/')
    operation = flask.request.form.get('operation')
    postid = flask.request.form.get('postid')
    # Bad request
    if not postid or not operation:
        flask.abort(400)
    # connect to the database
    connection = insta485.model.get_db()
    # check if the post is liked/unliked
    check_likes = "SELECT 1 FROM likes WHERE postid = ? AND owner = ?"
    cur_likes = connection.execute(
        check_likes,
        (postid, flask.session['username'])
    )
    already_like = cur_likes.fetchone() is not None
    if operation == 'like':
        if already_like:
            flask.abort(409)  # Conflict
        connection.execute(
            "INSERT INTO likes (postid, owner) VALUES (?,?)",
            (postid, flask.session['username'])
        )
    elif operation == 'unlike':
        if not already_like:
            flask.abort(409)  # Conflict
        connection.execute(
            "DELETE FROM likes WHERE postid =? AND owner =?",
            (postid, flask.session['username'])
        )
    else:
        flask.abort(400)  # Bad request

    return flask.redirect(target_url)
