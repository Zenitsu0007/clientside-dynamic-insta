"""
Insta485 index (main) view.

URLs include:
GET /
GET /uploads/<filename>
"""

import os
from flask import send_from_directory
import flask
import arrow
import insta485


@insta485.app.route('/', methods=['GET'])
def show_index():
    """Display / route."""
    # Check if user is logged in
    if 'username' not in flask.session:
        # Redirect to login page if not logged in
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    logname = flask.session['username']

    # Query database
    query = '''
        SELECT p.postid, p.filename as img_url, p.owner, u.filename
        as owner_img_url, p.created as timestamp
        FROM posts p
        JOIN users u ON p.owner = u.username
        WHERE p.owner = ? OR p.owner
        IN (SELECT username2 FROM following WHERE username1 = ?)
        ORDER BY p.created DESC, p.postid DESC
    '''
    cur = connection.execute(query, (logname, logname))
    posts = cur.fetchall()

    # Fetching likes for each post
    for post in posts:
        # Fetch likes
        like_query = '''
            SELECT COUNT(*) as like_count
            FROM likes WHERE postid = ?
        '''
        like_cur = connection.execute(like_query, (post['postid'],))
        post['likes'] = like_cur.fetchone()['like_count']
        # Determine whether I like this post
        like_query_bool = "SELECT 1 FROM likes WHERE postid = ? AND owner = ?"
        like_cur_bool = connection.execute(
            like_query_bool,
            (post['postid'], logname)
        )
        post['cur_liked'] = like_cur_bool.fetchone() is not None
        # Fetch comments
        comment_query = '''
            SELECT c.text, c.owner
            FROM comments c
            JOIN users u ON c.owner = u.username
            WHERE c.postid = ?
            ORDER BY c.created ASC
        '''
        comment_cur = connection.execute(comment_query, (post['postid'],))
        post['comments'] = comment_cur.fetchall()

        # Format timestamp
        post['timestamp'] = arrow.get(post['timestamp']).humanize()

    # Add database info to context
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)


# Reroute the file uploads.
@insta485.app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    """Display uploaded images."""
    # Check if the user is authenticated
    if 'username' not in flask.session:
        flask.abort(403)

    # Check if the file exists
    file_path = os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        flask.abort(404)

    # Return the file
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename)
