document.addEventListener('DOMContentLoaded', () => {
    const generateCsv = document.getElementById('generateCsv');
    const generateExcel = document.getElementById('generateExcel');
    const reportBody = document.getElementById('reportBody');

    async function loadReport() {
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        if (!start || !end) {
            reportBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:rgba(255,255,255,0.4);">Please select date range</td></tr>`;
            return;
        }
        const res = await fetch(`/api/attendance/report?start=${start}&end=${end}`);
        const data = await res.json();
        reportBody.innerHTML = '';
        if (data.records && data.records.length > 0) {
            data.records.forEach(r => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${r.student_id}</td><td>${r.name}</td><td>${r.date}</td><td>${r.time}</td><td>${(r.confidence * 100).toFixed(1)}%</td>`;
                reportBody.appendChild(tr);
            });
        } else {
            reportBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:rgba(255,255,255,0.4);">No records found</td></tr>`;
        }
    }

    document.getElementById('startDate').addEventListener('change', loadReport);
    document.getElementById('endDate').addEventListener('change', loadReport);

    generateCsv.addEventListener('click', async () => {
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        if (!start || !end) return alert('Select date range');
        const res = await fetch(`/api/attendance/export/csv?start=${start}&end=${end}`);
        const data = await res.json();
        alert('CSV exported: ' + data.file);
    });

    generateExcel.addEventListener('click', async () => {
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        if (!start || !end) return alert('Select date range');
        const res = await fetch(`/api/attendance/export/excel?start=${start}&end=${end}`);
        const data = await res.json();
        alert('Excel exported: ' + data.file);
    });
});
