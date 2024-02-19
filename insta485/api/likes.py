"""REST API for likes."""
import flask
import insta485

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    # Check authentication

    postid = flask.request.args.get('postid', type=int)
    if postid is None:
        flask.abort(400, description="Missing postid parameter")