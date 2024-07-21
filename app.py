import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Flask-Login ayarlar�
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Dummy user for authentication
class User(UserMixin):
    def __init__(self, username=None):
        self.username = username

    def get_id(self):
        return self.username

# Store usernames temporarily
users = set()
usernames = {}

# Dummy password
PASSWORD = 'caretaturan'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        if password == PASSWORD:
            user = User(username)
            login_user(user)
            usernames[username] = user
            return redirect(url_for('index'))
        else:
            return 'Invalid password', 403
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        uploaded_file.save(os.path.join('static', uploaded_file.filename))
        return 'File uploaded successfully'
    return render_template('upload.html')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    emit('message', {'username': username, 'message': message}, broadcast=True)

    if username not in users:
        users.add(username)

@app.route('/get_users', methods=['GET'])
@login_required
def get_users():
    return {'users': list(users)}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
