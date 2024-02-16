"""
Insta485 create account view.

URLs include:
GET /accounts/create/
"""
import flask
import insta485


@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    """Display the account creation page."""
    # Redirect to account edit page if user is already logged in
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    return flask.render_template("create.html")
