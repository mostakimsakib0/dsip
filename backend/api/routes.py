import base64
import cv2
import numpy as np
from flask import Blueprint, request, jsonify
from backend.face_recognition.recognizer import FaceRecognizer
from backend.database.db_manager import DatabaseManager
from backend.attendance.tracker import AttendanceTracker
from backend.attendance.report import ReportGenerator

api = Blueprint('api', __name__)
recognizer = FaceRecognizer()
db = DatabaseManager()
tracker = AttendanceTracker()
reporter = ReportGenerator()


@api.route('/recognize', methods=['POST'])
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
def get_students():
    students = db.get_all_students()
    return jsonify({
        'students': [
            {'student_id': s[0], 'name': s[1], 'department': s[2]}
            for s in students
        ]
    })


@api.route('/students/register', methods=['POST'])
def register_student():
    data = request.json
    sid = data.get('student_id')
    name = data.get('name')
    department = data.get('department')
    embedding = data.get('embedding')

    if not all([sid, name, department, embedding]):
        return jsonify({'error': 'Missing fields'}), 400

    db.register_student(sid, name, department, np.array(embedding))
    return jsonify({'message': 'Student registered successfully'})


@api.route('/attendance/today', methods=['GET'])
def today_attendance():
    summary = tracker.get_summary()
    return jsonify(summary)


@api.route('/attendance/report', methods=['GET'])
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
def export_csv():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end dates required'}), 400
    path = reporter.generate_csv(start, end)
    return jsonify({'file': path})


@api.route('/attendance/export/excel', methods=['GET'])
def export_excel():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end dates required'}), 400
    path = reporter.generate_excel(start, end)
    return jsonify({'file': path})
