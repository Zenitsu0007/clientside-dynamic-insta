"""REST API for comments."""
import flask
import insta485

@insta485.app.route("/api/v1/comments/", methods=["POST"])
def create_comment():
    """Create a new comment based on the text in the JSON body for the specified post id."""
    # HTTP authorization for user
    auth_response = insta485.api.index.check_authentication()
    if auth_response is not None:
        return auth_response

    # Extract username from session or basic auth
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']

    # Extract postid from query parameter and comment text from JSON body
    postid = flask.request.args.get('postid')
    text = flask.request.json.get('text')

    # Validate postid and text
    if not postid or not text:
        error_response = {"message": "Missing postid or text", "status_code": 400}
        return flask.jsonify(**error_response), 400

    # Connect to DB and check if post exists
    connection = insta485.model.get_db()
    post = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?",
        (postid,)
    ).fetchone()

    if not post:
        error_response = {"message": "Post not found", "status_code": 404}
        return flask.jsonify(**error_response), 404

    # Insert the new comment into the database
    cur = connection.execute(
        'INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)',
        (username, postid, text)
    )
    commentid = cur.lastrowid

    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": f"/users/{username}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }

    return flask.jsonify(**context), 201

@insta485.app.route("/api/v1/comments/<commentid>/", methods=["DELETE"])
def delete_comment():
    """Delete the comment based on the comment id."""
