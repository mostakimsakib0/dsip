async function loadDashboard() {
    try {
        const res = await fetch('/api/attendance/today');
        const data = await res.json();

        document.getElementById('presentToday').textContent = data.total || 0;

        const res2 = await fetch('/api/students');
        const students = await res2.json();
        document.getElementById('totalStudents').textContent = students.students?.length || 0;

        const total = students.students?.length || 1;
        const rate = ((data.total || 0) / total * 100).toFixed(1);
        document.getElementById('attendanceRate').textContent = rate + '%';

        const tbody = document.getElementById('attendanceBody');
        tbody.innerHTML = '';
        if (data.records && data.records.length > 0) {
            data.records.forEach(r => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${(r[3] * 100).toFixed(1)}%</td>`;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:rgba(255,255,255,0.4);">No attendance records yet</td></tr>`;
        }
    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setInterval(loadDashboard, 10000);
});
