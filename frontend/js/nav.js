/**
 * EduShield Shared Dynamic Navbar & Theme Engine
 */
document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Theme from localStorage
    const savedTheme = localStorage.getItem('edushield_theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    // 2. Render Shared Navbar
    const navContainer = document.getElementById('navbar-mount');
    if (navContainer) {
        const user = API.getUser();
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';

        const links = [
            { href: 'index.html', label: 'Home', icon: 'fa-home', publicOnly: false },
            { href: 'dashboard.html', label: 'Dashboard', icon: 'fa-chart-line', authRequired: true },
            { href: 'predict.html', label: 'Risk Assessment', icon: 'fa-user-check', authRequired: true },
            { href: 'history.html', label: 'Audit History', icon: 'fa-history', authRequired: true },
            { href: 'eda.html', label: 'Dataset & EDA', icon: 'fa-database', authRequired: false },
            { href: 'model_performance.html', label: 'Models Benchmark', icon: 'fa-microchip', authRequired: false },
            { href: 'about.html', label: 'About', icon: 'fa-info-circle', authRequired: false }
        ];

        let navLinksHtml = '';
        links.forEach(l => {
            if (l.authRequired && !user) return;
            const activeClass = (currentPage === l.href) ? 'active' : '';
            navLinksHtml += `
                <li class="nav-item">
                    <a class="nav-link ${activeClass}" href="${l.href}">
                        <i class="fas ${l.icon} me-1"></i>${l.label}
                    </a>
                </li>
            `;
        });

        let userAreaHtml = '';
        if (user) {
            userAreaHtml = `
                <div class="d-flex align-items-center gap-2">
                    <span class="badge ${user.role === 'admin' ? 'bg-danger' : 'bg-primary'} px-3 py-2 rounded-pill">
                        <i class="fas fa-user-shield me-1"></i>${user.username} (${user.role})
                    </span>
                    <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="API.logout()">
                        <i class="fas fa-sign-out-alt me-1"></i>Logout
                    </button>
                </div>
            `;
        } else {
            userAreaHtml = `
                <div class="d-flex align-items-center gap-2">
                    <a href="login.html" class="btn btn-outline-primary btn-sm rounded-pill px-3">
                        <i class="fas fa-sign-in-alt me-1"></i>Log In
                    </a>
                    <a href="register.html" class="btn btn-primary btn-sm rounded-pill px-3">
                        <i class="fas fa-user-plus me-1"></i>Register
                    </a>
                </div>
            `;
        }

        navContainer.innerHTML = `
            <nav class="navbar navbar-expand-lg navbar-top">
                <div class="container-fluid px-4">
                    <a class="navbar-brand d-flex align-items-center gap-2" href="index.html">
                        <img src="images/logo.png" alt="EduShield Logo" style="height: 38px; width: auto;" onerror="this.style.display='none'">
                        <span class="fw-bold" style="font-family: 'Outfit', sans-serif; letter-spacing: -0.5px; font-size: 1.35rem;">
                            Edu<span class="text-primary">Shield</span>
                        </span>
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#topNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="topNav">
                        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                            ${navLinksHtml}
                        </ul>
                        <div class="d-flex align-items-center gap-3">
                            <button class="btn btn-sm btn-light border rounded-circle theme-toggle-btn" id="themeToggle" title="Toggle Light/Dark Theme">
                                <i class="fas ${savedTheme === 'dark' ? 'fa-sun text-warning' : 'fa-moon text-secondary'}"></i>
                            </button>
                            <button class="btn btn-sm btn-light border rounded-circle" onclick="showBackendConfigModal()" title="Backend Connection Settings">
                                <i class="fas fa-cog text-muted"></i>
                            </button>
                            ${userAreaHtml}
                        </div>
                    </div>
                </div>
            </nav>
        `;

        // Theme Toggle Event Listener
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark-theme');
            localStorage.setItem('edushield_theme', isDark ? 'dark' : 'light');
            const icon = document.querySelector('#themeToggle i');
            if (icon) {
                icon.className = `fas ${isDark ? 'fa-sun text-warning' : 'fa-moon text-secondary'}`;
            }
        });
    }

    // 3. Auth Guard for Protected Pages
    const protectedPages = ['dashboard.html', 'predict.html', 'history.html'];
    const current = window.location.pathname.split('/').pop();
    if (protectedPages.includes(current)) {
        const user = API.getUser();
        if (!user) {
            window.location.href = `login.html?redirect=${encodeURIComponent(current)}`;
        }
    }
});

// Settings Modal for configuring Render Backend URL dynamically
window.showBackendConfigModal = function() {
    const currentBackend = CONFIG.API_BASE_URL;
    const modalHtml = `
        <div class="modal fade" id="backendModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg" style="border-radius: 16px;">
                    <div class="modal-header border-0 pb-0">
                        <h5 class="modal-title fw-bold"><i class="fas fa-server text-primary me-2"></i>Backend API Connection</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body py-3">
                        <p class="text-muted small">Current active backend endpoint used by this Vercel frontend:</p>
                        <div class="input-group mb-3">
                            <input type="text" id="customBackendInput" class="form-control" value="${currentBackend}" placeholder="https://your-render-app.onrender.com">
                            <button class="btn btn-outline-secondary" type="button" onclick="testBackendHealth()">Ping</button>
                        </div>
                        <div id="backendPingResult" class="small mb-2"></div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-primary rounded-pill px-3" onclick="saveCustomBackend()">Save & Reload</button>
                            <button class="btn btn-sm btn-light border rounded-pill px-3" onclick="resetCustomBackend()">Reset to Default</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    const existing = document.getElementById('backendModal');
    if (existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('backendModal'));
    modal.show();
};

window.testBackendHealth = async function() {
    const input = document.getElementById('customBackendInput').value.trim().replace(/\/+$/, '');
    const resDiv = document.getElementById('backendPingResult');
    resDiv.innerHTML = '<span class="text-info"><i class="fas fa-spinner fa-spin me-1"></i>Connecting...</span>';
    try {
        const res = await fetch(`${input}/api/health`, { method: 'GET' });
        const data = await res.json();
        resDiv.innerHTML = `<span class="text-success fw-bold"><i class="fas fa-check-circle me-1"></i>Connected! Status: ${data.status} (Model: ${data.best_model})</span>`;
    } catch (e) {
        resDiv.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Failed to reach backend: ${e.message}</span>`;
    }
};

window.saveCustomBackend = function() {
    const input = document.getElementById('customBackendInput').value.trim().replace(/\/+$/, '');
    if (input) {
        localStorage.setItem('edushield_custom_api', input);
        window.location.reload();
    }
};

window.resetCustomBackend = function() {
    localStorage.removeItem('edushield_custom_api');
    window.location.reload();
};
