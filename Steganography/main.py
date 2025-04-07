import base64
import os
import sqlite3

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from modes.Audio.audio import audio
from modes.Image.image import image
from modes.Text.text import text
from modes.Video.video import video

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
init_db()
UPLOAD_IMAGE_FOLDER = 'modes\\Image\\static'
IMAGE_CACHE_FOLDER = 'modes\\Image\\__pycache__'
UPLOAD_TEXT_FOLDER = 'modes\\Text\\static'
TEXT_CACHE_FOLDER = 'modes\\Text\\__pycache__'
UPLOAD_AUDIO_FOLDER = 'modes\\Audio\\static'
AUDIO_CACHE_FOLDER = 'modes\\Audio\\__pycache__'
UPLOAD_VIDEO_FOLDER = 'modes\\Video\\static'
VIDEO_CACHE_FOLDER = 'modes\\Video\\__pycache__'


# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = "hello"
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config['IMAGE_CACHE_FOLDER'] = IMAGE_CACHE_FOLDER
app.config['UPLOAD_TEXT_FOLDER'] = UPLOAD_TEXT_FOLDER
app.config['TEXT_CACHE_FOLDER'] = TEXT_CACHE_FOLDER
app.config['UPLOAD_AUDIO_FOLDER'] = UPLOAD_AUDIO_FOLDER
app.config['AUDIO_CACHE_FOLDER'] = AUDIO_CACHE_FOLDER
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER
app.config['VIDEO_CACHE_FOLDER'] = VIDEO_CACHE_FOLDER
app.register_blueprint(image, url_prefix="/image")
app.register_blueprint(audio, url_prefix="/audio")
app.register_blueprint(text, url_prefix="/text")
app.register_blueprint(video, url_prefix="/video")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        with sqlite3.connect('users.db') as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                flash("Registration successful! Please login.")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already taken.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                session['username'] = username
                return redirect(url_for('home'))
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAILERSEND_API_TOKEN = 'your_mailersend_api_token_here'

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        from_email = request.form['from_email']
        to_email = request.form['to_email']
        subject = request.form['subject']
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, 'rb') as f:
                file_data = f.read()
                encoded_file = base64.b64encode(file_data).decode('utf-8')

            response = requests.post(
                'https://api.mailersend.com/v1/email',
                headers={
                    'Authorization': f'Bearer {MAILERSEND_API_TOKEN}',
                    'Content-Type': 'application/json',
                },
                json={
                    "from": {"email": from_email, "name": "Steganography App"},
                    "to": [{"email": to_email}],
                    "subject": subject,
                    "text": "Please find your secret file attached.",
                    "attachments": [{
                        "filename": filename,
                        "content": encoded_file,
                        "disposition": "attachment"
                    }]
                }
            )

            if response.status_code == 202:
                flash("Email sent successfully!", "success")
            else:
                flash(f"Failed to send email: {response.text}", "danger")

            return redirect(url_for('send_email'))

    return render_template('send_email.html')


if __name__ == "__main__":
    app.run(debug=True)