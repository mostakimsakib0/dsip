document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('logout');
    if (el) {
        el.addEventListener('click', async e => {
            e.preventDefault();
            try { await fetch('/api/logout', { method: 'POST' }); } catch (_) {}
            window.location.href = '/';
        });
    }
});
