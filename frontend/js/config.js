/**
 * EduShield API Configuration
 * Automatically points to local Flask server during development,
 * and your Render production backend when deployed on Vercel.
 */
const CONFIG = {
    // Replace with your exact Render service URL once deployed on Render:
    RENDER_BACKEND_URL: "https://edushield-student-retention.onrender.com",
    LOCAL_BACKEND_URL: "http://127.0.0.1:5000",

    get API_BASE_URL() {
        // Priority 1: User custom override in localStorage
        const customUrl = localStorage.getItem('edushield_custom_api');
        if (customUrl) return customUrl.replace(/\/+$/, '');

        // Priority 2: Localhost testing
        const isLocal = window.location.hostname === 'localhost' || 
                        window.location.hostname === '127.0.0.1' ||
                        window.location.protocol === 'file:';
        if (isLocal) {
            return this.LOCAL_BACKEND_URL;
        }

        // Priority 3: Production Render backend
        return this.RENDER_BACKEND_URL;
    }
};

window.CONFIG = CONFIG;
