"""REST API for index."""
import hashlib
import flask
import insta485

@insta485.app.route("/api/v1/", methods=["GET"])
def get_index():
    """Return API resource URLs."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context), 200


def check_authentication():
    """Check authentication."""
    if flask.session:
        if 'username' not in flask.session:
            # Not logged in
            error_response = {'message': 'Forbidden', 'status_code': 403}
            return flask.jsonify(**error_response), 403
    elif flask.request.authorization:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        connection = insta485.model.get_db()

        # Fetch the stored password hash
        # (including the salt and algorithm) from the database
        query = 'SELECT password FROM users WHERE username = ?'
        cur = connection.execute(query, (username,))
        result = cur.fetchone()

        # If the user exists
        if result:
            stored_password = result['password']
            algorithm, salt, stored_hash = stored_password.split('$')
            # Hash the provided password
            # using the extracted salt (and algorithm)
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + password
            hash_obj.update(password_salted.encode('utf-8'))
            computed_hash = hash_obj.hexdigest()

            # Compare the computed hash with the stored hash
            if computed_hash != stored_hash:
                # Wrong password
                error_response = {'message': 'Forbidden', 'status_code': 403}
                return flask.jsonify(**error_response), 403
        else:
            # User not found
            error_response = {'message': 'Forbidden','status_code': 403}
            return flask.jsonify(**error_response), 403
    else:
        # Access without authentication
        error_response = {'message': 'Forbidden','status_code': 403}
        return flask.jsonify(**error_response), 403
    return None
