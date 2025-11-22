// API Client for Django CRM Backend

class APIClient {
    constructor() {
        this.baseURL = window.CRM_CONFIG.API_BASE_URL;
        this.token = localStorage.getItem(window.CRM_CONFIG.AUTH_TOKEN_KEY);
        this.isLoading = false;
    }

    // Get auth headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
        
        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }
        
        // Add CSRF token if available
        const csrfToken = this.getCSRFToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        return headers;
    }

    // Get CSRF token from cookie
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Build safe URL without duplicate slashes
    buildURL(endpoint) {
        const base = (this.baseURL || '').replace(/\/+$/, '');
        const path = String(endpoint || '');
        return `${base}${path.startsWith('/') ? '' : '/'}${path}`;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = this.buildURL(endpoint);
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            this.isLoading = true;
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorData;
                const contentType = response.headers.get('content-type');
                
                try {
                    if (contentType && contentType.includes('application/json')) {
                        errorData = await response.json();
                    } else {
                        errorData = { message: await response.text() };
                    }
                } catch (parseError) {
                    errorData = { message: `HTTP ${response.status}: ${response.statusText}` };
                }
                
                // Create detailed error object
                const apiError = new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
                apiError.status = response.status;
                apiError.data = errorData;
                apiError.url = url;
                apiError.endpoint = endpoint;
                
                throw apiError;
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            
            // Enhanced error with network detection
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                const networkError = new Error('Network error: Cannot connect to API server');
                networkError.type = 'network';
                networkError.url = url;
                this.handleError(networkError);
                throw networkError;
            }
            
            // Handle structured API errors
            if (error.status && error.data) {
                // Don't show error UI for 404s on dashboard endpoints - these are expected fallbacks
                const isDashboardFallback = error.endpoint && (
                    error.endpoint.includes('/dashboard/analytics') || 
                    error.endpoint.includes('/dashboard/activity') ||
                    error.endpoint.includes('/dashboard/stats')
                );
                
                if (!(error.status === 404 && isDashboardFallback)) {
                    this.handleError(error);
                }
            }
            
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    // Handle API errors
    handleError(error) {
        // Use the main app's error handling if available
        if (window.app && window.app.handleValidationError) {
            window.app.handleValidationError(error);
        } else {
            // Fallback error handling
            if (error.status === 401) {
                this.logout();
                this.showFallbackToast('Session expired. Please log in again.', 'error');
            } else if (error.status === 403) {
                this.showFallbackToast('Access denied', 'error');
            } else if (error.status === 404) {
                this.showFallbackToast('Resource not found', 'error');
            } else if (error.status >= 500) {
                this.showFallbackToast('Server error. Please try again later.', 'error');
            } else if (error.status === 400) {
                this.showFallbackToast('Validation error. Please check your input.', 'error');
            } else {
                this.showFallbackToast('Network error. Please check your connection.', 'error');
            }
        }
    }

    // Fallback toast for when main app is not available
    showFallbackToast(message, type) {
        if (window.app && window.app.showToast) {
            window.app.showToast(message, type);
        } else {
            // Simple alert fallback
            alert(`${type.toUpperCase()}: ${message}`);
        }
    }

    // Authentication methods
    async login(username, password) {
        try {
            const response = await this.request(window.CRM_CONFIG.ENDPOINTS.AUTH, {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            if (response.token) {
                this.token = response.token;
                localStorage.setItem(window.CRM_CONFIG.AUTH_TOKEN_KEY, this.token);
                return response;
            }
            throw new Error('Invalid credentials');
        } catch (error) {
            throw error;
        }
    }

    logout() {
        this.token = null;
        localStorage.removeItem(window.CRM_CONFIG.AUTH_TOKEN_KEY);
        window.location.reload();
    }

    // GET request
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return await this.request(url, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return await this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data) {
        return await this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // PATCH request
    async patch(endpoint, data) {
        return await this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return await this.request(endpoint, { method: 'DELETE' });
    }

    // Dashboard data (composite)
    async getDashboardData() {
        try {
            const dataPromises = [];
            const availableEndpoints = window.CRM_CONFIG.AVAILABLE_ENDPOINTS || [];
            const endpointMap = {
                contacts: window.CRM_CONFIG.ENDPOINTS.CONTACTS,
                companies: window.CRM_CONFIG.ENDPOINTS.COMPANIES,
                deals: window.CRM_CONFIG.ENDPOINTS.DEALS,
                leads: window.CRM_CONFIG.ENDPOINTS.LEADS,
                tasks: window.CRM_CONFIG.ENDPOINTS.TASKS
            };
            const availableData = {};
            for (const [key, endpoint] of Object.entries(endpointMap)) {
                if (availableEndpoints.includes(endpoint)) {
                    dataPromises.push(
                        this.get(endpoint, { limit: 10 })
                            .then(response => ({ key, data: response }))
                            .catch(() => ({ key, data: { results: [], count: 0 } }))
                    );
                } else {
                    availableData[key] = { results: [], count: 0 };
                }
            }
            dataPromises.push(
                this.getDashboardAnalytics()
                    .then(analytics => ({ key: 'analytics', data: analytics }))
                    .catch(() => ({ key: 'analytics', data: null }))
            );
            const results = await Promise.all(dataPromises);
            results.forEach(({ key, data }) => {
                if (key === 'analytics') {
                    availableData.analytics = data;
                } else {
                    availableData[key] = data.results || data;
                    availableData[`${key}Count`] = data.count || (data.results ? data.results.length : 0);
                }
            });
            return {
                contacts: availableData.contacts || [],
                companies: availableData.companies || [],
                deals: availableData.deals || [],
                leads: availableData.leads || [],
                tasks: availableData.tasks || [],
                analytics: availableData.analytics,
                stats: {
                    contactsCount: availableData.contactsCount || 0,
                    companiesCount: availableData.companiesCount || 0,
                    dealsCount: availableData.dealsCount || 0,
                    leadsCount: availableData.leadsCount || 0,
                    tasksCount: availableData.tasksCount || 0
                }
            };
        } catch (e) {
            console.warn('Failed to load dashboard data', e);
            return {
                contacts: [], companies: [], deals: [], leads: [], tasks: [], analytics: null,
                stats: { contactsCount: 0, companiesCount: 0, dealsCount: 0, leadsCount: 0, tasksCount: 0 }
            };
        }
    }

    // Dashboard analytics
    async getDashboardAnalytics() {
        try {
            return await this.get(window.CRM_CONFIG.ENDPOINTS.DASHBOARD_ANALYTICS);
        } catch (error) {
            if (error.status !== 404 && window.CRM_CONFIG?.DEBUG_MODE) {
                console.warn('Dashboard analytics endpoint not available, using fallback');
            }
            // Basic fallback
            return { monthly_growth: { contacts: 0, companies: 0, deals: 0 }, tasks: { active: 0, overdue: 0 } };
        }
    }

    // Activity feed
    async getActivityFeed(limit = 10) {
        try {
            return await this.get(window.CRM_CONFIG.ENDPOINTS.DASHBOARD_ACTIVITY, { limit });
        } catch (error) {
            if (error.status !== 404 && window.CRM_CONFIG?.DEBUG_MODE) {
                console.warn('Dashboard activity endpoint not available, fallback generation');
            }
            // Fallback: empty
            return [];
        }
    }
}

// Export singleton instance
window.apiClient = new APIClient();