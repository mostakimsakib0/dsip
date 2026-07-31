document.addEventListener('DOMContentLoaded', () => {
    const generateCsv = document.getElementById('generateCsv');
    const generateExcel = document.getElementById('generateExcel');
    const reportBody = document.getElementById('reportBody');

    function toInputDate(d) {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    const startInput = document.getElementById('startDate');
    const endInput = document.getElementById('endDate');
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 6);
    if (!startInput.value) startInput.value = toInputDate(weekAgo);
    if (!endInput.value) endInput.value = toInputDate(today);

    async function loadReport() {
        const start = startInput.value;
        const end = endInput.value;
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

    startInput.addEventListener('change', loadReport);
    endInput.addEventListener('change', loadReport);
    loadReport();
    setInterval(loadReport, 10000);

    generateCsv.addEventListener('click', async () => {
        const start = startInput.value;
        const end = endInput.value;
        if (!start || !end) return alert('Select date range');
        window.location.href = `/api/attendance/export/csv?start=${start}&end=${end}`;
    });

    generateExcel.addEventListener('click', async () => {
        const start = startInput.value;
        const end = endInput.value;
        if (!start || !end) return alert('Select date range');
        window.location.href = `/api/attendance/export/excel?start=${start}&end=${end}`;
    });
});
