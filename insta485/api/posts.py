"""REST API for posts."""
import hashlib
import flask
import insta485


@insta485.app.route('/api/v1/posts/', methods = ['GET'])
def get_post():
    """Return post on postid."""

    # HTTP authorization for user
    response = insta485.api.index.check_authentication()
    if response is not None:
        return response
    # If authorization successful, reads username from response
    username = response

    context = {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": "/posts/1/",
        "postid": "1",
        "url": flask.request.path,
    }
    return flask.jsonify(**context), 200
