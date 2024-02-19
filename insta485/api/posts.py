"""REST API for posts."""
import flask
import insta485


@insta485.app.route("/api/v1/posts/", methods = ["GET"])
def get_post_list():
    """Show a list of posts."""
    # HTTP authorization for user
    auth_response = insta485.api.index.check_authentication()
    if auth_response is not None:
        return auth_response

    # Extract username from session or basic auth
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']

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


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post_detail(postid_url_slug):
    """Show post detail by postid."""
    # HTTP authorization for user
    auth_response = insta485.api.index.check_authentication()
    if auth_response is not None:
        return auth_response

    # Extract username from session or basic auth
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']

    connection = insta485.model.get_db()

    # Check if the post exists
    post = connection.execute(
        'SELECT * FROM posts WHERE postid = ?', 
        (postid_url_slug,)
    ).fetchone()
    if not post:
        error_response = {"message": "Not Found", "status_code": 404}
        return flask.jsonify(**error_response), 404

    # Fetch comments for the post
    comments = connection.execute(
        'SELECT commentid, owner, text '
        'FROM comments WHERE postid = ?', 
        (postid_url_slug,)
    ).fetchall()
    comments_list = [
    {
        'commentid': comment['commentid'],
        'owner': comment['owner'],
        'text': comment['text'],
        'lognameOwnsThis': True if comment['owner'] == username else False,
        'url': f"/api/v1/comments/{comment['commentid']}/",
        'ownerShowUrl': f"/users/{comment['owner']}/"
    }
    for comment in comments
    ]

    # Fetch like details
    like = connection.execute(
        'SELECT likeid FROM likes WHERE owner = ? AND postid = ?', 
        (username, postid_url_slug)
    ).fetchone()
    num_likes = connection.execute(
        'SELECT COUNT(*) as count FROM likes WHERE postid = ?', 
        (postid_url_slug,)
    ).fetchone()['count']
    likes = {
        "lognameLikesThis": like is not None,
        "numLikes": num_likes,
        "url": f"/api/v1/likes/{like['likeid']}/" if like else None
    }

    owner_image_url = connection.execute(
        'SELECT filename FROM users WHERE username = ?', 
        (username,)
    ).fetchone()

    # Construct the response
    context = {
        "comments": comments_list,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": "",
        "imgUrl": f"/uploads/{post['filename']}",
        "likes": likes,
        "owner": post['owner'],
        "ownerImgUrl": f"/uploads/{owner_image_url['filename']}",
        "ownerShowUrl": f"/users/{post['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }

    return flask.jsonify(**context), 200
