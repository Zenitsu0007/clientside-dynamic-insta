"""REST API for posts."""
import hashlib
import os
import uuid
import arrow
import flask
import insta485
import sys


@insta485.app.route('/api/v1/posts/', methods = ['GET'])
def get_some_posts():
    """Return post on postid."""

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
    # We want posts 
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
    results = [{"postid": post_id, "url": f"/api/v1/posts/{post_id}/"} 
               for post_id in post_ids]
    # Current url
    url_now = flask.url_for("get_some_posts",
                        size=flask.request.args.get("size"),
                        page=flask.request.args.get("page"),
                        postid_lte=flask.request.args.get("postid_lte"))
    # Next field url
    if len(post_ids) < size:
      next_field =""
    else: 
      next_field = flask.url_for("get_some_posts",size=size,page=page + 1,
                        postid_lte=postid_lte)
    context = {
        "next": next_field,
        "results": results,
        "url": url_now
    }
    return flask.jsonify(**context), 200
    

@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    return 200