"""REST API for likes."""
import flask
import insta485

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    # Check authentication
    response = insta485.api.index.check_authentication()
    if response is not None:
        return response
    # If authorization successful, reads username from response
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']

    postid = flask.request.args.get('postid', type=int)
    if postid is None:
        return flask.jsonify({'message': 'Bad Request', 'status_code': '400'}), 400
    
    db = insta485.model.get_db()

    # Check if the post exists
    if not db.execute('SELECT 1 FROM posts WHERE postid = ?', (postid,)).fetchone():
        return flask.jsonify({"message": "Post not found", "status_code": 404}), 404
    
    # Check if the user has already liked the post
    query = 'SELECT likeid FROM likes WHERE owner = ? AND postid = ?'
    existing_like = db.execute(query, (username, postid)).fetchone()
    if existing_like:
        likeid = existing_like['likeid']
        context = {
            "likeid": likeid,
            "url": f"/api/v1/likes/{likeid}/"
        }
        return flask.jsonify(**context), 200
    
    # Create a new like
    query = 'INSERT INTO likes (owner, postid) VALUES (?, ?)'
    cur = db.execute(query, (username, postid))
    db.commit()

    query = 'SELECT likeid FROM likes WHERE owner = ? AND postid = ?'
    likeid = db.execute(query, (username, postid)).fetchone()['likeid']

    context = {
        "likeid": likeid,
        "url": f"/api/v1/likes/{likeid}/"
    }
    return flask.jsonify(**context), 201

@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete like."""
    # Check authentication
    response = insta485.api.index.check_authentication()
    if response is not None:
        return response
    # If authorization successful, reads username from response
    if 'username' in flask.session:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']
    
    db = insta485.model.get_db()
    query = 'SELECT owner, postid FROM likes WHERE likeid = ?'
    like = db.execute(query, (likeid,)).fetchone()
    if not like:
        return flask.jsonify({"message": "Like not found", "status_code": 404}), 404
    
    # Check if the user owns the like
    if like['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    # Delete the like
    query = 'DELETE FROM likes WHERE likeid = ? AND owner = ?'
    db.execute(query, (likeid, username))
    db.commit()

    return flask.jsonify({}), 204