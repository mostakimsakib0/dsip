import os
from functools import wraps
from flask import Flask, render_template, redirect, session, url_for
from flask_cors import CORS
from backend.api.routes import api

app = Flask(__name__, static_folder='../frontend',
            static_url_path='', template_folder='../frontend')
app.secret_key = os.environ.get('SECRET_KEY', 'smart-attendance-cse434-secret')
CORS(app, supports_credentials=True)
app.register_blueprint(api, url_prefix='/api')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/attendance')
@login_required
def attendance():
    return render_template('attendance.html')


@app.route('/register')
@login_required
def register():
    return render_template('register.html')


@app.route('/students')
@login_required
def students():
    return render_template('students.html')


@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
