import flask
import insta485

@insta485.app.route("/api/v1/comments/?postid=<postid>", methods=["POST"])
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


@insta485.app.route("/api/v1/comments/<commentid>/", methods=["DELETE"])
def delete_comment():
    """Delete the comment based on the comment id."""
