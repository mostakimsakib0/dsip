import base64
import cv2
import numpy as np
from functools import wraps
from flask import Blueprint, request, jsonify, send_file, session
from backend.face_recognition.recognizer import FaceRecognizer
from backend.database.db_manager import DatabaseManager
from backend.attendance.tracker import AttendanceTracker
from backend.attendance.report import ReportGenerator
from backend.config import SIMILARITY_THRESHOLD

api = Blueprint('api', __name__)
recognizer = FaceRecognizer()
db = DatabaseManager()
tracker = AttendanceTracker()
reporter = ReportGenerator()


def login_required_api(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Unauthorized'}), 401
        return view(*args, **kwargs)
    return wrapped


@api.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    row = db.verify_instructor(username, password)
    if not row:
        return jsonify({'error': 'Invalid username or password'}), 401
    session['logged_in'] = True
    session['username'] = row[0]
    session['full_name'] = row[1]
    return jsonify({'message': 'Login successful', 'username': row[0], 'full_name': row[1]})


@api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})


@api.route('/me', methods=['GET'])
def me():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'username': session['username'], 'full_name': session['full_name']})


def find_duplicate_face(embedding):
    known = db.get_all_embeddings()
    if not known:
        return None
    match = recognizer.matcher.find_best_match(embedding, known)
    if match and recognizer.matcher.is_recognized(match[2]):
        return match
    return None


@api.route('/recognize', methods=['POST'])
@login_required_api
def recognize():
    data = request.json
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'No image data'}), 400

    header, encoded = image_data.split(',', 1)
    binary = base64.b64decode(encoded)
    np_arr = np.frombuffer(binary, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    results = recognizer.recognize(frame)
    return jsonify({'faces': results})


@api.route('/students', methods=['GET'])
@login_required_api
def get_students():
    students = db.get_all_students()
    return jsonify({
        'students': [
            {'student_id': s[0], 'name': s[1], 'department': s[2]}
            for s in students
        ]
    })


@api.route('/students/<student_id>', methods=['DELETE'])
@login_required_api
def delete_student(student_id):
    deleted = db.delete_student(student_id)
    if deleted == 0:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'message': f'Student {student_id} deleted'})


@api.route('/students/register', methods=['POST'])
@login_required_api
def register_student():
    data = request.json
    sid = data.get('student_id')
    name = data.get('name')
    department = data.get('department')
    image_data = data.get('image')
    embedding = data.get('embedding')

    if not all([sid, name, department]):
        return jsonify({'error': 'Missing fields'}), 400

    existing = db.student_exists(sid)
    if existing:
        return jsonify({
            'error': f'Student {sid} ({existing}) is already registered'
        }), 409

    if embedding is not None:
        emb = np.array(embedding, dtype=np.float32)
        dup = find_duplicate_face(emb)
        if dup:
            return jsonify({
                'error': f'This face already belongs to {dup[1]} ({dup[0]})'
            }), 409
        db.register_student(sid, name, department, emb)
        return jsonify({'message': 'Student registered successfully'})

    if not image_data:
        return jsonify({'error': 'Missing face image or embedding'}), 400

    try:
        header, encoded = image_data.split(',', 1)
        binary = base64.b64decode(encoded)
        np_arr = np.frombuffer(binary, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        return jsonify({'error': 'Invalid image data'}), 400

    if frame is None:
        return jsonify({'error': 'Could not decode image'}), 400

    frame = recognizer.preprocess(frame)
    faces = recognizer.detector.detect(frame)
    if len(faces) == 0:
        return jsonify({'error': 'No face detected in the image'}), 400
    if len(faces) > 1:
        return jsonify({'error': 'Multiple faces detected. Use a single-face image.'}), 400

    emb = recognizer.embedder.extract_embedding(faces[0])
    dup = find_duplicate_face(emb)
    if dup:
        return jsonify({
            'error': f'This face already belongs to {dup[1]} ({dup[0]})'
        }), 409
    db.register_student(sid, name, department, emb)
    return jsonify({'message': 'Student registered successfully'})


@api.route('/attendance/today', methods=['GET'])
@login_required_api
def today_attendance():
    summary = tracker.get_summary()
    return jsonify(summary)


@api.route('/attendance/report', methods=['GET'])
@login_required_api
def attendance_report():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end dates required'}), 400
    records = tracker.get_report(start, end)
    return jsonify({
        'records': [
            {'student_id': r[0], 'name': r[1], 'date': r[2], 'time': r[3], 'confidence': r[4]}
            for r in records
        ]
    })


@api.route('/attendance/export/csv', methods=['GET'])
@login_required_api
def export_csv():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end dates required'}), 400
    path = reporter.generate_csv(start, end)
    return send_file(path, as_attachment=True, download_name=f'attendance_{start}_to_{end}.csv')


@api.route('/attendance/export/excel', methods=['GET'])
@login_required_api
def export_excel():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end dates required'}), 400
    path = reporter.generate_excel(start, end)
    return send_file(path, as_attachment=True, download_name=f'attendance_{start}_to_{end}.xlsx')
