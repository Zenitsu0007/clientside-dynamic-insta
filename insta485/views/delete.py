"""
Insta485 Delete account view.

URLs include:
GET /accounts/delete/
"""
import flask
import insta485


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    """Display the account deletion page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    logname = flask.session['username']

    # Render the deletion page if GET request
    return flask.render_template("delete.html", logname=logname)
