"""REST API for posts."""
import os
import uuid
import arrow
import flask
import insta485


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    # Check authentication
    if 'username' not in flask.session:
        # Redirect to login page if not logged in
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    # Query for post details
    query = '''
        SELECT p.postid, p.filename as img_url,
                p.created as timestamp,
                p.owner, u.filename as owner_img_url,
                (SELECT COUNT(*) FROM likes WHERE postid = p.postid) as likes
        FROM posts p
        JOIN users u ON p.owner = u.username
        WHERE p.postid = ?
    '''
    cur = connection.execute(query, (postid_url_slug,))
    post = cur.fetchone()
    like_query_bool = "SELECT 1 FROM likes WHERE postid = ? AND owner = ?"
    like_cur_bool = connection.execute(
        like_query_bool,
        (post['postid'], logname)
    )
    post['cur_liked'] = like_cur_bool.fetchone() is not None
    
    # Query for comments and check if the comment is owned by the logged user
    comment_query = '''
        SELECT *,
            CASE WHEN c.owner = ? THEN 1 ELSE 0 END as is_owned
        FROM comments c
        WHERE c.postid = ?
        ORDER BY c.created ASC
    '''
    comments_query = connection.execute(
        comment_query,
        (logname, postid_url_slug)
    )
    comments = comments_query.fetchall()
    # Format timestamp
    post['timestamp'] = arrow.get(post['timestamp']).humanize()
    context = {
        "logname": logname,
        "post": post,
        "comments": comments
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/')
def get_top_posts():
    """Return 10 newest posts made by logged-in user or who they follow."""
    # Check authentication
    if 'username' not in flask.session:
        # Redirect to login page if not logged in
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']

    postid_limit = request.args.get('postid_lte',
                                    default=sys.maxsize, type=int)
    size = request.args.get('size', default=10, type=int)
    page = request.args.get('page', default=0, type=int)

    if size < 0 or page < 0:
        raise invalid_usage.InvalidUsage('Bad Request', status_code=400)

    results = insta485.model.query_db(
        "SELECT DISTINCT p.postid "
        "FROM posts p, following f "
        "WHERE (p.owner == ? "
        "OR (f.username1 == ? "
        "AND f.username2 == p.owner)) "
        "AND p.postid <= ?"
        "ORDER BY p.postid DESC "
        "LIMIT ? "
        "OFFSET ?",
        (username, username, postid_limit, size, size * page,)
    )

    latest_postid = request.args.get("postid_lte")
    if results and (not latest_postid):
        latest_postid = max(item["postid"] for item in results)
    for item in results:
        postid = item["postid"]
        item["url"] = f"/api/v1/posts/{postid}/"

    # next field
    next_field = ""
    if len(results) >= size:
        next_field = url_for("get_top_posts",
                             size=size,
                             page=page + 1,
                             postid_lte=latest_postid)

    context = {
        "next": next_field,
        "results": results,
        "url": url_for("get_top_posts",
                       size=request.args.get("size"),
                       page=request.args.get("page"),
                       postid_lte=request.args.get("postid_lte"))
    }
    return flask.jsonify(**context), 200

