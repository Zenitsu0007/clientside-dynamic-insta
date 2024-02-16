"""
Insta485 posts view.

URLs include:
GET /posts/<postid_url_slug>/
"""
import os
import uuid
import arrow
import flask
import insta485


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Display a specific post."""
    connection = insta485.model.get_db()
    # Check if user is logged in
    if 'username' not in flask.session:
        # Redirect to login page if not logged in
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    # Query for post details
    query = '''
        SELECT p.postid, p.filename as img_url, p.created as timestamp,
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
    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def create_delete_post():
    """Create and delete posts."""
    # Redirect to login page if not logged in
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    # Delete post comments
    target_url = flask.request.args.get('target', f'/users/{logname}/')
    operation = flask.request.form.get('operation')
    postid = flask.request.form.get('postid')
    connection = insta485.model.get_db()
    if operation == 'delete' and postid is not None:
        # check if the post is owned by the logged user
        post_owner_query = "SELECT * FROM posts WHERE postid = ? AND owner = ?"
        post_owner = connection.execute(post_owner_query, (postid, logname))
        post_delete = post_owner.fetchone()
        if post_delete is None:
            flask.abort(403)
        # Delete the image file
        image_path = os.path.join(
            insta485.app.config['UPLOAD_FOLDER'],
            post_delete['filename']
        )
        if os.path.exists(image_path):
            os.remove(image_path)
        # Delete the post
        connection.execute(
            "DELETE FROM posts WHERE postid = ?",
            (postid,))
        return flask.redirect(target_url)

    if operation == 'create':
        # Extract the data
        fileobj = flask.request.files['file']
        filename = fileobj.filename
        if filename == '':
            flask.abort(400)
        # UUID
        stem = uuid.uuid4().hex
        suffix = os.path.splitext(filename)[1].lower()
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config['UPLOAD_FOLDER']/uuid_basename
        fileobj.save(path)
        # Insert the post into the database
        connection.execute(
            "INSERT INTO posts (filename, owner) VALUES (?, ?)",
            (uuid_basename, logname))
        connection.commit()
        target_url = flask.url_for('show_user', user_url_slug=logname)
        return flask.redirect(target_url)

    return flask.redirect(target_url)
