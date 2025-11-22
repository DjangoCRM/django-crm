// Global CRM configuration
window.CRM_CONFIG = {
    // API settings
    API_BASE_URL: 'http://127.0.0.1:8000/api/',
    AUTH_TOKEN_KEY: 'crm_token',
    REQUEST_TIMEOUT: 30000, // 30 seconds

    // Application settings
    DEBUG_MODE: true, // Shows console logs for debugging

    // Endpoints
    ENDPOINTS: {
        AUTH: 'auth/token/',
        USER_PROFILE: 'users/me/',
        CONTACTS: 'contacts/',
        COMPANIES: 'companies/',
        DEALS: 'deals/',
        LEADS: 'leads/',
        TASKS: 'tasks/',
        PROJECTS: 'projects/',
        MEMOS: 'memos/',
        CHAT_MESSAGES: 'chat-messages/',
        DASHBOARD_ANALYTICS: 'dashboard/analytics/',
        DASHBOARD_ACTIVITY: 'dashboard/activity/',
        DASHBOARD_STATS: 'dashboard/stats/'
    },

    // List of available API endpoints in the Django backend
    AVAILABLE_ENDPOINTS: [
        'contacts/',
        'companies/',
        'deals/',
        'leads/',
        'projects/',
        'tasks/',
        'memos/',
        'chat-messages/',
        'dashboard/analytics/',
        'dashboard/activity/',
        'dashboard/stats/',
    ],
    
    // Dashboard settings
    DASHBOARD: {
        AUTO_REFRESH_INTERVAL: 60000, // 60 seconds
    }
};
