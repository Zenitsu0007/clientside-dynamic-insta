"""
Insta485 Auth check.

URLs include:
GET /accounts/auth/

"""
import flask
import insta485


@insta485.app.route('/accounts/auth/', methods=['GET'])
def auth_check():
    """Auth check used in AWS delpoyment."""
    # Check if the user is already logged in
    if 'username' in flask.session:
        return ('', 200)
    flask.abort(403)
