"""
Insta485 comments.

URLs include:
/comments/?target=URL
"""
import flask
import insta485


@insta485.app.route('/comments/', methods=['POST'])
def add_delete_comments():
    """Add_comments or delete comments."""
    # Redirect to login page if not logged in
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    target_url = flask.request.args.get('target', '/')
    operation = flask.request.form.get('operation')
    comment_id = flask.request.form.get('commentid')
    postid = flask.request.form.get('postid')
    text = flask.request.form.get('text')
    # connect to the database
    connection = insta485.model.get_db()
    if operation == 'create':
        # check if the text if empty or the postid is not given
        if not text or not postid:
            flask.abort(400)
        else:
            connection.execute(
                "INSERT INTO comments ( owner, postid, text ) VALUES (?,?,?)",
                (logname, postid, text)
            )
    elif operation == 'delete':
        # check if the comment is this logged user's
        check_result = connection.execute(
            '''SELECT * FROM comments
            WHERE owner = ? AND commentid = ?''',
            (logname, comment_id)).fetchone()
        if check_result is None:
            flask.abort(403)
        else:
            connection.execute(
                "DELETE FROM comments WHERE commentid = ? ",
                (comment_id,)
            )
    else:
        flask.abort(400)  # Bad request
    return flask.redirect(target_url)
