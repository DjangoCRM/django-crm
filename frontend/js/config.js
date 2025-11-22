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
        AUTH: 'v1/auth/token/',
        USER_PROFILE: 'v1/users/me/',
        CONTACTS: 'v1/contacts/',
        COMPANIES: 'v1/companies/',
        DEALS: 'v1/deals/',
        LEADS: 'v1/leads/',
        TASKS: 'v1/tasks/',
        PROJECTS: 'v1/projects/',
        DASHBOARD_ANALYTICS: 'v1/dashboard/analytics/',
        DASHBOARD_ACTIVITY: 'v1/dashboard/activity/',
        DASHBOARD_STATS: 'v1/dashboard/stats/'
    },

    // List of available API endpoints in the Django backend
    AVAILABLE_ENDPOINTS: [
        '/v1/contacts/',
        '/v1/companies/',
        '/v1/deals/',
        '/v1/leads/',
        '/v1/projects/',
        '/v1/tasks/',
        '/v1/dashboard/analytics/',
        '/v1/dashboard/activity/',
        '/v1/dashboard/stats/',
    ],
    
    // Dashboard settings
    DASHBOARD: {
        AUTO_REFRESH_INTERVAL: 60000, // 60 seconds
    }
};
