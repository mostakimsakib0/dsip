const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusText = document.getElementById('statusText');
const logDiv = document.getElementById('recognitionLog');

let stream = null;
let interval = null;
let running = false;
const lastMarked = {};

function log(message) {
    const p = document.createElement('div');
    p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logDiv.appendChild(p);
    logDiv.scrollTop = logDiv.scrollHeight;
}

function drawBoxes(faces) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scaleX = canvas.width / video.videoWidth;
    const scaleY = canvas.height / video.videoHeight;

    faces.forEach(face => {
        const [x1, y1, x2, y2] = face.bbox;
        const known = !!face.student_id;
        ctx.strokeStyle = known ? '#00e676' : '#ff5252';
        ctx.lineWidth = 3;
        ctx.strokeRect(x1 * scaleX, y1 * scaleY, (x2 - x1) * scaleX, (y2 - y1) * scaleY);

        const label = known
            ? `${face.name} ${(face.confidence * 100).toFixed(1)}%`
            : 'Unknown';
        ctx.font = 'bold 16px Segoe UI, sans-serif';
        const tw = ctx.measureText(label).width + 12;
        const ly = y1 * scaleY > 24 ? y1 * scaleY - 24 : y1 * scaleY;
        ctx.fillStyle = known ? '#00e676' : '#ff5252';
        ctx.fillRect(x1 * scaleX, ly, tw, 22);
        ctx.fillStyle = '#000';
        ctx.fillText(label, x1 * scaleX + 6, ly + 16);
    });
}

startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        video.srcObject = stream;
        await video.play();
        running = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusText.textContent = 'Camera is active';
        log('Camera started, detecting faces...');

        interval = setInterval(captureAndRecognize, 1500);
    } catch (err) {
        statusText.textContent = 'Error: Camera access denied';
        log('Error: ' + err.message);
    }
});

stopBtn.addEventListener('click', () => {
    running = false;
    if (interval) clearInterval(interval);
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
    video.srcObject = null;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusText.textContent = 'Camera is off';
    log('Camera stopped');
});

async function captureAndRecognize() {
    if (!stream || !running) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.drawImage(video, 0, 0);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);

    try {
        const res = await fetch('/api/recognize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl })
        });
        const data = await res.json();

        if (data.faces && data.faces.length > 0) {
            drawBoxes(data.faces);
            const now = Date.now();
            data.faces.forEach(face => {
                if (face.student_id) {
                    if (face.attended) {
                        lastMarked[face.student_id] = now;
                        log(`✓ ${face.name} (${face.student_id}) - attendance marked [${(face.confidence * 100).toFixed(1)}%]`);
                    } else if (!lastMarked[face.student_id] || now - lastMarked[face.student_id] > 60000) {
                        lastMarked[face.student_id] = now;
                        log(`✓ ${face.name} (${face.student_id}) - already marked [${(face.confidence * 100).toFixed(1)}%]`);
                    }
                } else {
                    log(`? Unknown person detected`);
                }
            });
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            log('No faces detected');
        }
    } catch (err) {
        log('Recognition error: ' + err.message);
    }
}
