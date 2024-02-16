"""
Insta485 explore view.

URLs include:
GET /explore/
"""
import flask
import insta485


@insta485.app.route('/explore/', methods=['GET'])
def explore():
    """Display the explore page."""
    connection = insta485.model.get_db()

    logname = flask.session.get('username')

    # Query for users not followed by logname
    query = '''
        SELECT u.username, u.filename as user_img_url
        FROM users u
        WHERE u.username != ?
        AND u.username NOT IN (
            SELECT username2 FROM following WHERE username1 = ?
        )
    '''
    not_following = connection.execute(query, (logname, logname)).fetchall()

    context = {
        "logname": logname,
        "not_following": not_following
    }
    return flask.render_template("explore.html", **context)
