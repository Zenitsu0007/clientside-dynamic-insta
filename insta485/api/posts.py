"""REST API for posts."""
import sys
import flask
import insta485


@insta485.app.route("/api/v1/posts/", methods = ["GET"])
def get_some_posts():
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

    # Get arguments
    postid_lte = flask.request.args.get('postid_lte', default=sys.maxsize, type=int)
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    # Check if page and size are valid
    if size <= 0 or page < 0:
        error_response = {"message": "Bad Request","status_code": "400"}
        return flask.jsonify(error_response), 400
    # Connect to the database
    connection = insta485.model.get_db()
    query = '''
    SELECT DISTINCT p.postid
    FROM posts p
    LEFT JOIN following f ON f.username2 = p.owner
    WHERE p.postid <= ? AND (f.username1 = ? OR p.owner = ?)
    ORDER BY p.postid DESC
    LIMIT ? OFFSET ?
    '''
    cur = connection.execute(query, (postid_lte,username, username, size, size*page))
    posts = cur.fetchall()
    post_ids = [item['postid'] for item in posts]
    # latest post id
    if not flask.request.args.get("postid_lte") and post_ids:
        postid_lte = max(post_ids)
    # Construct results
    results = [{"postid": post_id, "url": f"/api/v1/posts/{post_id}/"} for post_id in post_ids]
    # Current url
    url_now = flask.url_for("get_some_posts",
                        size=flask.request.args.get("size"),
                        page=flask.request.args.get("page"),
                        postid_lte=flask.request.args.get("postid_lte"))
    # Next field url
    if len(post_ids) < size:
        next_field =""
    else:
        next_field = flask.url_for("get_some_posts",size=size,page=page + 1, postid_lte=postid_lte)
    context = {
        "next": next_field,
        "results": results,
        "url": url_now
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
        "created": post['created'],
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
