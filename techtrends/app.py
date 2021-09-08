import sqlite3 #Module of pyhton to create database web aplication
#Resource:: https://www.javatpoint.com/flask-sqlite
import logging
import sys

#First we will run python __init__.py because __init__.py serves double duty: it will contain
# the application factory, and it tells Python that the flaskr directory should be treated as a package
#https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    global total_db_count #https://www.w3schools.com/python/python_variables_global.asp
    total_db_count +=1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
total_db_count=0 #To find total number of database connections made.

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('A non-existing article is accessed and a 404 page is returned.')
      return render_template('404.html'), 404
    else:
      app.logger.info('An existing article is retrieved with title :'+post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The about us page is retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            
            app.logger.info('A new article is created with title :' + title)
            return redirect(url_for('index'))

    return render_template('create.html')
    
@app.route('/healtz')
def healthcheck():
    '''Return health of application'''
    con = get_db_connection()
    print('Connection opened successfully')
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Status request successfull')
    return response
    
@app.route('/metrics')
def metrics():
    '''Return metrics(total users and database connections) of application'''
    con = get_db_connection()
    print('Connection opened successfully')
    con_result=con.execute('SELECT COUNT(*) from posts').fetchone()[0]
    print(con_result)
    response = app.response_class(
            response=json.dumps({"status":"success","data":{"db_connection_count":total_db_count,"post_count":con_result}}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":
    # Create a custom logger
    logger = logging.getLogger(__name__)
    #Resource::https://www.toptal.com/python/in-depth-python-logging
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d/%d-%yyyy %H:%M:%S',level=logging.DEBUG)
    s_handler = logging.StreamHandler(sys.stdout)
    e_handler = logging.StreamHandler(sys.stderr)

    # Add handlers to the logger
    logger.addHandler(s_handler)
    logger.addHandler(e_handler)

    app.run(host='0.0.0.0', port='3111')
    