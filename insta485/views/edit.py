"""
Insta485 Edit account view.

URLs include:
GET /accounts/edit/
"""
import flask
import insta485


@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit():
    """Edit account page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    logname = flask.session['username']
    connection = insta485.model.get_db()
    # get user info
    cur = connection.execute(
        "SELECT fullname, email, filename FROM users WHERE username = ?",
        (logname,)
    )
    user_info = cur.fetchone()

    return flask.render_template(
        "edit.html",
        logname=logname,
        user_info=user_info
    )
