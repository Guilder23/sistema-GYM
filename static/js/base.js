// Funciones JavaScript para la interfaz

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}

function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

// Cerrar dropdowns al hacer click fuera
document.addEventListener('click', function(e) {
    const navbar = document.querySelector('.navbar');
    if (navbar && !e.target.closest('.navbar-item')) {
        const notifDropdown = document.getElementById('notificationDropdown');
        const userDropdown = document.getElementById('userDropdown');
        if (notifDropdown) notifDropdown.style.display = 'none';
        if (userDropdown) userDropdown.style.display = 'none';
    }
});

// Cerrar alertas
document.querySelectorAll('.alert .close').forEach(btn => {
    btn.addEventListener('click', function() {
        this.closest('.alert').remove();
    });
});

const themeToggleBtn = document.getElementById('themeToggle');
if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
}

// Auto cerrar alertas después de 5 segundos
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.remove();
    });
}, 5000);
