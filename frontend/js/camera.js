const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusText = document.getElementById('statusText');
const logDiv = document.getElementById('recognitionLog');

let stream = null;
let interval = null;

function log(message) {
    const p = document.createElement('div');
    p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logDiv.appendChild(p);
    logDiv.scrollTop = logDiv.scrollHeight;
}

startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        video.srcObject = stream;
        await video.play();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusText.textContent = 'Camera is active';
        log('Camera started, detecting faces...');

        interval = setInterval(captureAndRecognize, 2000);
    } catch (err) {
        statusText.textContent = 'Error: Camera access denied';
        log('Error: ' + err.message);
    }
});

stopBtn.addEventListener('click', () => {
    if (interval) clearInterval(interval);
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
    video.srcObject = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusText.textContent = 'Camera is off';
    log('Camera stopped');
});

async function captureAndRecognize() {
    if (!stream) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg');

    try {
        const res = await fetch('/api/recognize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl })
        });
        const data = await res.json();

        if (data.faces && data.faces.length > 0) {
            data.faces.forEach(face => {
                if (face.student_id) {
                    const status = face.attended ? 'marked' : 'already marked';
                    log(`✓ ${face.name} (${face.student_id}) - ${status} [${(face.confidence * 100).toFixed(1)}%]`);
                } else {
                    log(`? Unknown person detected`);
                }
            });
        } else {
            log('No faces detected');
        }
    } catch (err) {
        log('Recognition error: ' + err.message);
    }
}
