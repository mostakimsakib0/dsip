from flask import Flask, render_template
from flask_cors import CORS
from backend.api.routes import api

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)
app.register_blueprint(api, url_prefix='/api')


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/attendance')
def attendance():
    return render_template('attendance.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
