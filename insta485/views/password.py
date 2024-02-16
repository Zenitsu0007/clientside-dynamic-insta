"""
Insta485 password view.

URLs include:
GET /accounts/password/
"""
import flask
import insta485


@insta485.app.route('/accounts/password/', methods=['GET'])
def password():
    """Update password page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("password.html", **context)
