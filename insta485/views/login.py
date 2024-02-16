"""
Insta485 Login view.

URLs include:
GET /accounts/login/
"""
import flask
import insta485


@insta485.app.route('/accounts/login/', methods=['GET'])
def login():
    """Display the login page and handle login requests."""
    # If the user is already logged in, redirect to the main page
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Render the login page if GET request or login failed
    return flask.render_template("login.html")
