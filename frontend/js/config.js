// Configuration for Business CRM Frontend

const CRM_CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://127.0.0.1:8000/api',
    
    // Development vs Production
    ENVIRONMENT: 'development',
    
    // CORS Settings
    CORS_ENABLED: true,
    
    // Authentication
    AUTH_TOKEN_KEY: 'crm_token',
    AUTH_REFRESH_INTERVAL: 15 * 60 * 1000, // 15 minutes
    
    // API Timeouts
    REQUEST_TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    
    // Phone/VoIP Configuration
    VOIP_ENABLED: true,
    VOIP_SERVER: 'ws://127.0.0.1:8000/ws/voip/',
    
    // UI Configuration
    TOAST_DURATION: 5000,
    LOADING_DELAY: 300,
    
    // Debug Settings
    DEBUG_MODE: true,
    CONSOLE_LOGS: true,
    
    // Endpoints
    ENDPOINTS: {
        AUTH: '/v1/auth/token/',
        USER_PROFILE: '/v1/users/me/',
        CONTACTS: '/v1/contacts/',
        COMPANIES: '/v1/companies/',
        LEADS: '/v1/leads/',
        DEALS: '/v1/deals/',
        TASKS: '/v1/tasks/',
        PROJECTS: '/v1/projects/',
        VOIP_STATUS: '/voip/status/',
        VOIP_CALL: '/voip/call/'
    }
};

// Environment-specific overrides
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    CRM_CONFIG.DEBUG_MODE = true;
    CRM_CONFIG.CONSOLE_LOGS = true;
} else {
    CRM_CONFIG.DEBUG_MODE = false;
    CRM_CONFIG.CONSOLE_LOGS = false;
    CRM_CONFIG.API_BASE_URL = window.location.origin + '/api';
}

// Export configuration
window.CRM_CONFIG = CRM_CONFIG;