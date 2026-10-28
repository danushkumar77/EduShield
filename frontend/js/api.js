/**
 * EduShield API Client
 * Interacts with Render Flask backend with automatic token handling
 */
const API = {
    getToken() {
        return localStorage.getItem('edushield_token');
    },

    setToken(token) {
        if (token) localStorage.setItem('edushield_token', token);
        else localStorage.removeItem('edushield_token');
    },

    getUser() {
        try {
            return JSON.parse(localStorage.getItem('edushield_user') || 'null');
        } catch {
            return null;
        }
    },

    setUser(user) {
        if (user) localStorage.setItem('edushield_user', JSON.stringify(user));
        else localStorage.removeItem('edushield_user');
    },

    logout() {
        this.setToken(null);
        this.setUser(null);
        window.location.href = 'login.html';
    },

    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const headers = {
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        try {
            const res = await fetch(url, { ...options, headers });
            
            if (res.status === 401 && !endpoint.includes('/login') && !endpoint.includes('/register')) {
                // Token expired
                this.logout();
                throw new Error("Session expired. Please log in again.");
            }

            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                throw new Error(data.error || `Server responded with status ${res.status}`);
            }
            return data;
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            throw err;
        }
    },

    // --- Authentication ---
    async login(username, password) {
        const res = await this.request('/api/auth/login', {
            method: 'POST',
            body: { username, password }
        });
        if (res.token) this.setToken(res.token);
        if (res.user) this.setUser(res.user);
        return res;
    },

    async register(username, email, password, role = 'user') {
        const res = await this.request('/api/auth/register', {
            method: 'POST',
            body: { username, email, password, role }
        });
        if (res.token) this.setToken(res.token);
        if (res.user) this.setUser(res.user);
        return res;
    },

    async getMe() {
        return await this.request('/api/auth/me');
    },

    // --- Analytics & Predictions ---
    async getDashboardStats() {
        return await this.request('/api/dashboard/stats');
    },

    async predict(formData) {
        return await this.request('/api/predict', {
            method: 'POST',
            body: formData
        });
    },

    async getPredictions(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`/api/predictions?${query}`);
    },

    async getPrediction(id) {
        return await this.request(`/api/predictions/${id}`);
    },

    async deletePrediction(id) {
        return await this.request(`/api/predictions/${id}`, {
            method: 'DELETE'
        });
    },

    async getModels() {
        return await this.request('/api/models');
    },

    async getEdaSummary() {
        return await this.request('/api/eda/summary');
    },

    async getHealth() {
        return await this.request('/api/health');
    }
};

window.API = API;
