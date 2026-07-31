const studentBody = document.getElementById('studentBody');
const logoutLink = document.getElementById('logout');

async function loadStudents() {
    studentBody.innerHTML = `<tr><td colspan="4" class="empty">Loading...</td></tr>`;
    try {
        const res = await fetch('/api/students');
        if (!res.ok) return window.location.href = '/';
        const data = await res.json();
        studentBody.innerHTML = '';
        if (data.students && data.students.length > 0) {
            data.students.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.student_id}</td>
                    <td>${s.name}</td>
                    <td>${s.department}</td>
                    <td><button class="btn btn-danger" data-id="${s.student_id}" data-name="${s.name}">Delete</button></td>`;
                studentBody.appendChild(tr);
            });
            studentBody.querySelectorAll('.btn-danger').forEach(btn => {
                btn.addEventListener('click', () => deleteStudent(btn.dataset.id, btn.dataset.name));
            });
        } else {
            studentBody.innerHTML = `<tr><td colspan="4" class="empty">No students registered yet</td></tr>`;
        }
    } catch (err) {
        studentBody.innerHTML = `<tr><td colspan="4" class="empty">Failed to load students: ${err.message}</td></tr>`;
    }
}

async function deleteStudent(id, name) {
    if (!confirm(`Delete ${name} (${id}) and their attendance records?`)) return;
    try {
        const res = await fetch(`/api/students/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            loadStudents();
        } else {
            alert(data.error || 'Delete failed');
        }
    } catch (err) {
        alert('Delete error: ' + err.message);
    }
}

logoutLink.addEventListener('click', async e => {
    e.preventDefault();
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/';
});

document.addEventListener('DOMContentLoaded', loadStudents);
