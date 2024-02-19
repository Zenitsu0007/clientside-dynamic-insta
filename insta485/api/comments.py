import flask
import insta485

@insta485.app.route("/api/v1/comments/?postid=<postid>", methods=["POST"])
def create_comment():
    """Create a new comment based on the text in the JSON body for the specified post id."""



@insta485.app.route("/api/v1/comments/<commentid>/", methods=["DELETE"])
def delete_comment():
    """Delete the comment based on the comment id."""
