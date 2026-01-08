from flask import Flask, request, render_template, redirect, Response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin
from uuid import uuid4
from bot import admin_bot
from threading import Thread
import sqlite3
from hashlib import sha256
from setup_db import init_db
import socket
import os
from flask import render_template_string
import ipaddress
import random
import string
import requests
import time
app = Flask(__name__)
app.config['SESSION_COOKIE_HTTPONLY'] = False
login_manager = LoginManager()
app.secret_key = 'SecRes{2nd_flag_lfi_source_leak}'
login_manager.init_app(app)

# Generate a random authentication token for internal services
AUTH_TOKEN = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(42))


init_db()


DB_FILE = "nexus.db"

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()


# User model compatible with Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, password, is_admin=0):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.posts = {}

    @staticmethod
    def get(user_id):
        """Retrieve a user from the database by ID."""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, password, is_admin FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                user = User(row[0], row[1], row[2], row[3], row[4])
                cursor.execute("SELECT id, title, content FROM posts WHERE user_id = ?", (user_id,))
                posts = cursor.fetchall()
                user.posts = {post_id: {"title": title, "content": content} for post_id, title, content in posts}
                return user
        return None

    @staticmethod
    def get_by_username(username):
        """Retrieve a user from the database by username."""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, password, is_admin FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                user = User(row[0], row[1], row[2], row[3], row[4])
                cursor.execute("SELECT id, title, content FROM posts WHERE user_id = ?", (user.username,))
                posts = cursor.fetchall()
                user.posts = {post_id: {"title": title, "content": content} for post_id, title, content in posts}
                return user
        return None

    @staticmethod
    def get_posts(user_id):
        """Retrieve all posts for a user."""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM posts WHERE user_id = ?", (user_id,))
            posts = cursor.fetchall()
            return {post_id: {"title": title, "content": content} for post_id, title, content in posts}


    def is_authenticated(self):
        return True

    def __str__(self):
        return f"{self.id}, {self.username}, {self.email}, {self.password}, {self.posts}"


@login_manager.user_loader
def user_loader(user_id):
    return User.get(user_id)

@app.before_first_request
def init_app():
    logout_user()


@app.route('/')
def index():
    return redirect('/home')

@app.route('/docs')
def docs():
    return render_template('api_docs.html')


@app.route('/home')
def home():
    if current_user.is_authenticated:
        return Response(render_template('home.html', user=current_user), status=200, content_type='text/html')
    else: return Response(render_template('home.html'), status=200, content_type='text/html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)
        # hash password and compare with stored hash
        hashed_password = sha256(password.encode()).hexdigest()
        if user and user.password == hashed_password:
            login_user(user)
            return redirect('/home')
        return Response(render_template('login.html', error='Invalid username or password'), status=400, content_type='text/html')
    return Response(render_template('login.html'), status=200, content_type='text/html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # hash password before storing
        password = sha256(password.encode()).hexdigest()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 0)", (username, email, password))
                conn.commit()
                return redirect('/login')
            except sqlite3.IntegrityError:
                return Response(render_template('register.html', error='Username already exists'), status=400, content_type='text/html')
    return Response(render_template('register.html'), status=200, content_type='text/html')



@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (title, content, current_user.id))
            conn.commit()
            cursor.execute("SELECT id, title, content FROM posts WHERE user_id = ?", (current_user.id,))
            posts = cursor.fetchall()
            post_id = posts[-1][0]
        return Response(render_template('createpost.html', post_id=post_id), content_type='text/html')
    return Response(render_template('createpost.html'), content_type='text/html')


@app.route('/view/<int:post_id>')
@login_required
def view(post_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT posts.title, posts.content, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.id = ?
        """, (post_id,))
        post = cursor.fetchone()
        post = {"title": post[0], "content": post[1]}
        if not post:
            return Response(render_template('view.html', error="Post not found"), status=404, content_type='text/html')
        
        return Response(render_template('view.html', post_id=post_id, post=post), status=200, content_type='text/html')

# route for showing all created posts of the current user
@app.route('/myposts')
@login_required
def myposts():
    user_id = current_user.id
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM posts WHERE user_id = ?", (user_id,))
        posts = cursor.fetchall()
        posts = [{"id": post[0], "title": post[1], "content": post[2]} for post in posts]
    return Response(render_template('myposts.html', posts=posts), status=200, content_type='text/html')

# Report route
@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        link = request.form.get('url')
        if not link or not link.startswith('http'):
            return Response(render_template('report.html', error='No valid link provided'), status=404, content_type='text/html')
        
        # Trigger the report handling bot
        try:
            Thread(target=admin_bot, args=(link,)).start()
        except Exception as e:
            print(e)
            return Response(render_template('report.html', error='Error occurred while submitting report'), status=404, content_type='text/html')

        return Response(render_template('report.html', message='Report submitted successfully'), status=200, content_type='text/html')

    return Response(render_template('report.html'), status=200, content_type='text/html')


@app.route('/make_admin', methods=['GET', 'POST'])
@login_required
def make_admin():
    if not current_user.is_admin:
        return Response("Unauthorized", status=403)
    

    username = request.values.get('username')
    if username:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
            conn.commit()
        return redirect('/admin')
    return redirect('/home')

# Admin route
@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect('/home')  # Only accessible by the admin user

    url = request.args.get('url')
    logfile = request.args.get('logfile')
    output = ""
    error = ""
    file_content = ""
    
    if logfile:
        # Local File Inclusion
        try:
            with open(logfile, 'r') as f:
                file_content = f.read()
        except Exception as e:
            error = f"Error reading log: {str(e)}"
    
    if url:
        try:

            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url

            # 1. Parse URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            # 2. DNS Resolution (Security Check)
            # We resolve the IP to check if it's GLOBAL (Public).
            ip = None
            try:
                ip = socket.gethostbyname(hostname)
                ip_obj = ipaddress.ip_address(ip)
                is_safe = ip_obj.is_global
            except Exception as e:
                is_safe = False
            
            if not is_safe:
                error = f"Security Alert: access to internal/private IP {ip or 'unknown'} is forbidden."
            else:
                time.sleep(2) # cooldown 
                resp = requests.get(url, timeout=5, headers={'X-Nexus-Token': AUTH_TOKEN})
                output = resp.text
                
        except Exception as e:
            error = f"Error fetching URL: {str(e)}"
        
    return Response(render_template('admin.html', output=output, url=url, error=error, file_content=file_content, logfile=logfile), status=200, content_type='text/html')

# Internal Healthcheck Endpoint - Localhost Only
@app.route('/healthcheck')
def healthcheck():
    # Protection: Only allow requests from localhost
    if request.remote_addr != '127.0.0.1':
        return Response("Access Denied", status=403)
    
    # Protection: Require the internal AUTH_TOKEN
    # This ensures only the 'External Link Scanner' (or someone who knows the token) can access this.
    token = request.headers.get('X-Nexus-Token')
    if not token or token != AUTH_TOKEN:
        return Response("Access Denied: Missing or Invalid Internal Token", status=403)
    
    cmd = request.args.get('cmd')
    if cmd:

        return os.popen(cmd).read()
    
    return "System Status: OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)