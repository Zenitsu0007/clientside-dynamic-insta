"""
Insta485 accounts view.

URLs include:
POST /accounts/?target=URL
"""
import pathlib
import uuid
import hashlib
import os
import flask
import insta485


def hash_password(password):
    """Hash password."""
    # Hash the password
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def login(connection, target_url):
    """Login accounts."""
    # Get the username and password from the form
    username = flask.request.form['username']
    password = flask.request.form['password']
    # Check if username or password fields are empty
    if not username or not password:
        flask.abort(400)  # Bad request

    # Fetch the stored password hash
    # (including the salt and algorithm) from the database
    query1 = 'SELECT password FROM users WHERE username = ?'
    cur = connection.execute(query1, (username,))
    result1 = cur.fetchone()

    # If the user exists
    if result1:
        stored_password = result1['password']
        algorithm, salt, stored_hash = stored_password.split('$')
        # Hash the provided password
        # using the extracted salt (and algorithm)
        hash_obj1 = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj1.update(password_salted.encode('utf-8'))
        computed_hash = hash_obj1.hexdigest()

        # Compare the computed hash with the stored hash
        if computed_hash == stored_hash:
            # Authentication successful
            flask.session['username'] = username
            return flask.redirect(target_url)
        flask.abort(403)  # Forbidden
    else:
        # User not found
        flask.abort(403)  # Forbidden


def create(connection, target_url):
    """Create accounts."""
    # Extract the data
    fullname = flask.request.form['fullname']
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']

    # Handle profile photo upload
    fileobj = flask.request.files['file']

    # Check if all fields are filled in
    if (not fullname or not username or not email or
            not password or not fileobj):
        flask.abort(400)  # Bad request

    filename = fileobj.filename

    password_db_string = hash_password(password)

    # UUID
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config['UPLOAD_FOLDER']/uuid_basename
    fileobj.save(path)

    # check if username already exists
    user = connection.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,)).fetchone()
    if user:
        flask.abort(409)

    # insert user into database
    connection.execute('''
        INSERT INTO users (username, fullname, email, filename, password)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, fullname, email, uuid_basename, password_db_string)
    )
    connection.commit()

    flask.session['username'] = username

    return flask.redirect(target_url)


def delete(connection, target_url):
    """Delete accounts."""
    # Check if user is logged in
    if 'username' not in flask.session:
        flask.abort(403)  # User not logged in

    username = flask.session['username']

    # Delete images
    post_query = "SELECT filename FROM posts WHERE owner=?"
    post_images = connection.execute(post_query, (username, ))
    delete_images = post_images.fetchall()
    for row in delete_images:
        filename = row['filename']
        path = os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)

    # Perform the deletion
    query = '''
        DELETE FROM users WHERE username = ?
    '''
    connection.execute(query, (username,))
    connection.commit()

    # Clear the session
    flask.session.clear()
    return flask.redirect(target_url)


def edit_account(connection, target_url):
    """Edit accounts."""
    # Check if user is logged in
    if 'username' not in flask.session:
        flask.abort(403)  # User not logged in

    username = flask.session['username']

    # process data
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']

    if not fullname or not email:
        flask.abort(400)  # Bad request

    # process image
    fileobj = flask.request.files['file']
    filename = fileobj.filename

    if fileobj and filename != '':
        # UUID
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config['UPLOAD_FOLDER']/uuid_basename
        fileobj.save(path)

        # update database
        query = '''
            UPDATE users
            SET fullname = ?, email = ?, filename = ?
            WHERE username = ?
        '''
        connection.execute(
            query,
            (fullname, email, uuid_basename, username)
        )
    else:
        # update user info without changing image
        query = '''
            UPDATE users
            SET fullname = ?, email = ?
            WHERE username = ?
        '''
        connection.execute(query, (fullname, email, username))
    connection.commit()
    # Clear session
    return flask.redirect(target_url)


def password_update(connection, target_url):
    """Password update for accounts."""
    # Check if user is logged in
    if 'username' not in flask.session:
        flask.abort(403)
    logname = flask.session['username']
    # Read form data
    oldpassword = flask.request.form.get('password')
    newpassword1 = flask.request.form.get('new_password1')
    newpassword2 = flask.request.form.get('new_password2')
    # Check empty
    if not oldpassword or not newpassword1 or not newpassword2:
        flask.abort(400)
    # Connect to database and hash the oldpassword
    connection = insta485.model.get_db()
    password_in_db = hash_password(oldpassword)
    # Verify oldpassword
    result = connection.execute('''
    SELECT password FROM users WHERE username = ?
    ''', (logname,)).fetchone()
    verify_password = result['password']
    algorithm, salt, verify_hash = verify_password.split('$')
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + oldpassword
    hash_obj.update(password_salted.encode('utf-8'))
    password_in_db = hash_obj.hexdigest()
    if verify_hash != password_in_db:
        flask.abort(403)
    # Verify newpassword match
    if newpassword1 != newpassword2:
        flask.abort(401)
    # Hash newpassword
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + newpassword1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_in_db = "$".join([algorithm, salt, password_hash])
    # Update password
    connection.execute('''
        UPDATE users
        SET password =?
        WHERE username =?
    ''', (password_in_db, logname))
    connection.commit()
    # Clear session
    return flask.redirect(target_url)


@insta485.app.route('/accounts/', methods=['POST'])
def account_operation():
    """Login, create, edit, delete and password update for accounts."""
    target_url = flask.request.args.get('target', '/')
    operation = flask.request.form.get('operation')
    connection = insta485.model.get_db()
    if operation == 'login':
        return login(connection, target_url)
    if operation == 'create':
        return create(connection, target_url)
    if operation == 'delete':
        return delete(connection, target_url)
    if operation == 'edit_account':
        return edit_account(connection, target_url)
    if operation == 'update_password':
        return password_update(connection, target_url)
    flask.abort(400)
