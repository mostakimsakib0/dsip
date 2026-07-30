# Smart Attendance System With Face Recognition

**CSE434: Digital Signal and Image Processing**

A real-time face recognition-based attendance system using InsightFace's Buffalo_L model.

## Features

- Real-time face detection and recognition via webcam
- 512-dimensional face embedding extraction (Buffalo_L)
- Cosine similarity-based identity matching
- Automatic attendance recording with duplicate detection
- Attendance dashboard with live statistics
- Report generation (CSV / Excel)
- Student registration with face enrollment

## Architecture

```
backend/
├── api/           # Flask REST API + WebSocket
├── attendance/    # Tracking & report generation
├── database/      # SQLite schema & operations
└── face_recognition/  # Detection, embedding, matching

frontend/
├── css/           # Styling
├── js/            # Client logic
├── login.html     # Instructor login
├── register.html  # Student registration
├── dashboard.html # Attendance dashboard
├── attendance.html# Live camera view
└── reports.html   # Report generation UI
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m backend.app
```

Visit `http://localhost:5000` in your browser.

## Team

| Member | Role |
|--------|------|
| Ahmad Hasan Mubashshir | Face Recognition, Backend, System Integration |
| Md. Mostakim Ahmed Sakib | Frontend, Dashboard, Login/Registration, DB Integration |
| Md. Saiful Islam | Database Design, Attendance Management, Testing, Documentation |
