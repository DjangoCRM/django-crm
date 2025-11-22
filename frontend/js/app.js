// Django CRM Frontend Application
class CRMApp {
    constructor() {
        // Use configuration from config.js
        this.apiBase = window.CRM_CONFIG.API_BASE_URL;
        this.token = localStorage.getItem(window.CRM_CONFIG.AUTH_TOKEN_KEY);
        this.currentUser = null;
        this.currentSection = 'dashboard';
        this.dashboardRefreshInterval = null;
        this.lastDashboardUpdate = null;

        // Debug info
        if (window.CRM_CONFIG.DEBUG_MODE) {
            console.log('🚀 CRM App initialized');
            console.log('📡 API Base:', this.apiBase);
            console.log('🔐 Token exists:', !!this.token);
        }

        // Initialize component managers
        this.contacts = new ContactManager(this);
        this.companies = new CompanyManager(this);
        this.deals = new DealManager(this);
        this.tasks = new TaskManager(this);
        this.leads = new LeadManager(this);
        this.projects = new ProjectManager(this);
        this.memos = new MemoManager(this);
        this.chat = new ChatManager(this);
        this.phone = new PhoneManager(this);
        this.components = new ComponentManager(this);

        this.defineActionHandlers();
        this.init();
    }

    defineActionHandlers() {
        this.actionHandlers = {
            'phone.closeWidget': () => this.phone.closeWidget(),
            'phone.dialer.digit': (target) => this.phone.dialer.addDigit(target.dataset.digit),
            'phone.call': () => this.phone.startCall(),
            'phone.dialer.clear': () => this.phone.dialer.clearNumber(),
            'phone.mute': () => this.phone.muteCall(),
            'phone.hold': () => this.phone.holdCall(),
            'phone.hangup': () => this.phone.endCall(),
            'phone.openDialer': () => this.phone.openDialer(),
            'togglePasswordVisibility': () => togglePasswordVisibility(),
            'contacts.showContactForm': (target) => this.contacts.showContactForm(target.dataset.id),
            'contacts.viewContact': (target) => this.contacts.viewContact(target.dataset.id),
            'contacts.editContact': (target) => this.contacts.editContact(target.dataset.id),
            'contacts.deleteContact': (target) => this.contacts.deleteContact(target.dataset.id),
            'contact.closeContactForm': () => document.getElementById('contact-modal').remove(),
            'contact.closeViewContactModal': () => document.getElementById('contact-view-modal').remove(),
            'companies.showCompanyForm': (target) => this.companies.showCompanyForm(target.dataset.id),
            'companies.viewCompany': (target) => this.companies.viewCompany(target.dataset.id),
            'companies.editCompany': (target) => this.companies.editCompany(target.dataset.id),
            'companies.deleteCompany': (target) => this.companies.deleteCompany(target.dataset.id),
            'companies.closeCompanyForm': () => document.getElementById('company-modal').remove(),
            'companies.closeViewCompanyModal': () => document.getElementById('company-view-modal').remove(),
            'refreshDashboard': () => this.refreshDashboard(),
            'switchSection': (target) => this.switchSection(target.dataset.section),
        };
    }

    init() {
        this.setupEventListeners();
        if (this.token) {
            this.checkAuthStatus();
            this.loadSection('dashboard');
            document.querySelector('main').style.display = 'block';
            document.querySelector('aside').style.display = 'block';
        } else {
            this.showLoginModal();
            document.querySelector('main').style.display = 'none';
            document.querySelector('aside').style.display = 'none';
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget?.dataset?.section || btn.dataset.section;
                if (section) this.switchSection(section);
            });
        });

        // Login modal
        document.getElementById('login-btn').addEventListener('click', () => {
            this.showLoginModal();
        });

        document.getElementById('cancel-login').addEventListener('click', () => {
            this.hideLoginModal();
        });

        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // HTMX events
        document.addEventListener('htmx:beforeRequest', (e) => {
            if (this.token) {
                e.detail.xhr.setRequestHeader('Authorization', `Token ${this.token}`);
            }
        });

        document.addEventListener('htmx:responseError', (e) => {
            if (e.detail.xhr.status === 401) {
                this.handleAuthError();
            } else {
                this.showToast('Error: ' + e.detail.xhr.statusText, 'error');
            }
        });

        // Universal handler for data-action attributes
        document.body.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;
            const handler = this.actionHandlers[action];

            if (handler) {
                // Pass the target element to the handler, which can then extract data-id or other attributes
                handler(target);
            } else if (window.CRM_CONFIG.DEBUG_MODE) {
                console.warn(`No handler found for action: ${action}`);
            }
        });


        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('aside');
        const mainContent = document.querySelector('main');
        const sidebarToggleButtonIcon = sidebarToggle.querySelector('i');

        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('body-content-collapsed');
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));

            if (sidebar.classList.contains('collapsed')) {
                sidebarToggleButtonIcon.classList.remove('fa-chevron-left');
                sidebarToggleButtonIcon.classList.add('fa-chevron-right');
            } else {
                sidebarToggleButtonIcon.classList.remove('fa-chevron-right');
                sidebarToggleButtonIcon.classList.add('fa-chevron-left');
            }
        });

        if (localStorage.getItem('sidebar-collapsed') === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('body-content-collapsed');
            sidebarToggleButtonIcon.classList.remove('fa-chevron-left');
            sidebarToggleButtonIcon.classList.add('fa-chevron-right');
        }
    }

    async checkAuthStatus() {
        if (!this.token) {
            document.getElementById('auth-status').innerHTML =
                '<span class="text-gray-500">Not logged in</span>';
            return;
        }

        try {
            const response = await window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.USER_PROFILE);
            this.currentUser = response;
            document.getElementById('auth-status').innerHTML =
                `<div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-medium">
                        ${(response.first_name || '').charAt(0)}${(response.last_name || '').charAt(0)}
                    </div>
                    <span class="text-gray-700 font-medium">${response.first_name} ${response.last_name}</span>
                </div>`;

            const loginBtn = document.getElementById('login-btn');
            loginBtn.innerHTML = '<i class="fas fa-sign-out-alt mr-2"></i>Logout';
            loginBtn.onclick = () => this.logout();

            // Load counts for sidebar
            this.updateSidebarCounts();
        } catch (error) {
            this.handleAuthError();
        }
    }

    async updateSidebarCounts() {
        try {
            const countPromises = [];
            const endpoints = {
                contacts: window.CRM_CONFIG.ENDPOINTS.CONTACTS,
                companies: window.CRM_CONFIG.ENDPOINTS.COMPANIES,
                leads: window.CRM_CONFIG.ENDPOINTS.LEADS,
                deals: window.CRM_CONFIG.ENDPOINTS.DEALS,
                tasks: window.CRM_CONFIG.ENDPOINTS.TASKS
            };

            // Only make requests to available endpoints
            Object.entries(endpoints).forEach(([key, endpoint]) => {
                if (this.isEndpointAvailable(endpoint)) {
                    countPromises.push(
                        window.apiClient.get(endpoint, { limit: 1 })
                            .then(response => ({ key, count: response.count || 0 }))
                            .catch(error => {
                                console.warn(`Error fetching ${key} count:`, error);
                                return { key, count: 0 };
                            })
                    );
                } else {
                    // Set count to 0 for unavailable endpoints
                    countPromises.push(Promise.resolve({ key, count: 0 }));
                }
            });

            const results = await Promise.all(countPromises);

            // Update sidebar counts
            results.forEach(({ key, count }) => {
                const countElement = document.getElementById(`${key}-count`);
                if (countElement) {
                    countElement.textContent = count;

                    // Add visual indicator for unavailable modules
                    const navBtn = document.querySelector(`[data-section="${key}"]`);
                    if (navBtn && count === 0 && !this.isEndpointAvailable(endpoints[key])) {
                        navBtn.classList.add('opacity-60');
                        navBtn.title = `${key.charAt(0).toUpperCase() + key.slice(1)} module not available`;
                    }
                }
            });

        } catch (error) {
            console.error('Error updating sidebar counts:', error);
            // Set all counts to 0 on error
            ['contacts', 'companies', 'leads', 'deals', 'tasks'].forEach(key => {
                const countElement = document.getElementById(`${key}-count`);
                if (countElement) {
                    countElement.textContent = '0';
                }
            });
        }
    }

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await window.apiClient.login(username, password);

            if (response.token) {
                this.token = response.token;
                this.hideLoginModal();
                this.checkAuthStatus();
                this.loadSection(this.currentSection);
                document.querySelector('main').style.display = 'block';
                document.querySelector('aside').style.display = 'block';
                this.showToast('Logged in successfully', 'success');
            } else {
                this.showToast('Invalid credentials', 'error');
            }
        } catch (error) {
            this.showToast('Login failed', 'error');
        }
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('crm_token');
        document.getElementById('auth-status').innerHTML =
            '<span class="text-gray-500">Not logged in</span>';

        const loginBtn = document.getElementById('login-btn');
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i>Login';
        loginBtn.onclick = () => this.showLoginModal();

        // Reset sidebar counts
        document.querySelectorAll('[id$="-count"]').forEach(el => {
            el.textContent = '0';
        });

        this.showLoginModal();
        document.querySelector('main').style.display = 'none';
        document.querySelector('aside').style.display = 'none';
        this.showToast('Logged out successfully', 'success');
    }

    handleAuthError() {
        this.logout();
        this.showToast('Authentication expired. Please log in again.', 'error');
    }

    showLoginModal() {
        const modal = document.getElementById('login-modal');
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.add('is-open');
            modal.querySelector('.scale-95').classList.add('scale-100');
        }, 50);
    }

    hideLoginModal() {
        const modal = document.getElementById('login-modal');
        modal.classList.remove('is-open');
        modal.querySelector('.scale-95').classList.remove('scale-100');
        setTimeout(() => {
            modal.classList.add('hidden');
            document.getElementById('login-form').reset();
        }, 300);
    }

    switchSection(section) {
        // Update navigation - new sidebar style
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('bg-primary', 'bg-opacity-10', 'text-primary', 'font-semibold');
            btn.classList.add('text-gray-600', 'hover:bg-gray-100', 'hover:text-gray-900', 'font-medium');

            // Update icons
            const icon = btn.querySelector('i');
            if (icon) {
                icon.classList.remove('text-primary');
                icon.classList.add('text-gray-400', 'group-hover:text-gray-600');
            }
        });

        const activeBtn = document.querySelector(`[data-section="${section}"]`);
        if (activeBtn) {
            activeBtn.classList.remove('text-gray-600', 'hover:bg-gray-100', 'hover:text-gray-900', 'font-medium');
            activeBtn.classList.add('bg-primary', 'bg-opacity-10', 'text-primary', 'font-semibold');

            // Update icon
            const icon = activeBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('text-gray-400', 'group-hover:text-gray-600');
                icon.classList.add('text-primary');
            }
        }

        // Update breadcrumb
        const safeSection = section || this.currentSection || 'dashboard';
document.getElementById('current-section').textContent = this.getSectionTitle(safeSection);

        // Show/hide sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.add('hidden');
            sec.classList.remove('active');
        });

        const targetSection = document.getElementById(`${section}-section`);
        if (!targetSection) {
            console.warn('Section container not found:', section);
            return;
        }
        targetSection.classList.remove('hidden');
        targetSection.classList.add('active');

        // Handle dashboard auto-refresh
        if (section === 'dashboard') {
            this.startDashboardAutoRefresh();
        } else {
            this.stopDashboardAutoRefresh();
        }

        this.currentSection = section;
        this.loadSection(section);
    }

    // Dashboard auto-refresh methods
    startDashboardAutoRefresh() {
        if (this.dashboardRefreshInterval) {
            clearInterval(this.dashboardRefreshInterval);
        }

        if (window.CRM_CONFIG?.DASHBOARD?.AUTO_REFRESH_INTERVAL && this.token) {
            this.dashboardRefreshInterval = setInterval(() => {
                if (this.currentSection === 'dashboard' && this.token) {
                    this.refreshDashboard();
                }
            }, window.CRM_CONFIG.DASHBOARD.AUTO_REFRESH_INTERVAL);

            if (window.CRM_CONFIG?.DEBUG_MODE) {
                console.log('🔄 Dashboard auto-refresh started');
            }
        }
    }

    stopDashboardAutoRefresh() {
        if (this.dashboardRefreshInterval) {
            clearInterval(this.dashboardRefreshInterval);
            this.dashboardRefreshInterval = null;

            if (window.CRM_CONFIG?.DEBUG_MODE) {
                console.log('⏹️ Dashboard auto-refresh stopped');
            }
        }
    }

    // Refresh dashboard without full reload
    async refreshDashboard() {
        if (!this.token || this.currentSection !== 'dashboard') {
            return;
        }

        try {
            // Update only the data, keep the UI structure
            const dashboardData = await window.apiClient.getDashboardData();
            const activityFeed = await window.apiClient.getActivityFeed(6);

            if (dashboardData) {
                this.updateDashboardCounts(dashboardData.stats);
                this.updateDashboardActivity(activityFeed);
                this.lastDashboardUpdate = new Date();

                // Show refresh indicator
                this.showRefreshIndicator();
            }
        } catch (error) {
            console.warn('Dashboard refresh failed:', error);
        }
    }

    // Update dashboard counts without full reload
    updateDashboardCounts(stats) {
        if (!stats) return;

        const countElements = {
            'contacts': stats.contactsCount,
            'companies': stats.companiesCount,
            'deals': stats.dealsCount,
            'tasks': stats.tasksCount
        };

        Object.entries(countElements).forEach(([type, count]) => {
            const element = document.querySelector(`[onclick="app.switchSection('${type}')"] .text-2xl`);
            if (element && element.textContent !== count.toString()) {
                element.textContent = count;
                // Add animation for changed values
                element.classList.add('animate-pulse');
                setTimeout(() => element.classList.remove('animate-pulse'), 1000);
            }
        });
    }

    // Update activity feed without full reload
    updateDashboardActivity(activities) {
        const activityContainer = document.querySelector('.space-y-4:last-child');
        if (!activityContainer || !activities) return;

        if (activities.length > 0) {
            const newContent = activities.map(activity => {
                const timeAgo = this.formatTimeAgo(activity.timestamp);
                const colorClass = activity.color || 'primary';
                return `
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 bg-${colorClass} bg-opacity-10 rounded-full flex items-center justify-center">
                            <i class="${activity.icon} text-${colorClass} text-xs"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm text-gray-900">${activity.message}</p>
                            <p class="text-xs text-gray-500">${timeAgo}</p>
                        </div>
                    </div>
                `;
            }).join('');

            activityContainer.innerHTML = newContent;
        }
    }

    // Show refresh indicator
    showRefreshIndicator() {
        const refreshBtn = document.querySelector('.fa-sync-alt');
        if (refreshBtn) {
            refreshBtn.classList.add('animate-spin');
            setTimeout(() => {
                refreshBtn.classList.remove('animate-spin');
            }, 1000);
        }
    }

    // Proxy API call to window.apiClient for backward compatibility
    apiCall(url, options = {}) {
        const method = (options.method || 'GET').toUpperCase();
        const parseBody = (b) => typeof b === 'string' ? JSON.parse(b) : (b || {});
        if (method === 'GET') return window.apiClient.get(url);
        if (method === 'POST') return window.apiClient.post(url, parseBody(options.body));
        if (method === 'PUT') return window.apiClient.put(url, parseBody(options.body));
        if (method === 'PATCH') return window.apiClient.patch(url, parseBody(options.body));
        if (method === 'DELETE') return window.apiClient.delete(url);
        return window.apiClient.request(url, options);
    }

    getSectionTitle(section) {
        const titles = {
            'dashboard': 'Home',
            'contacts': 'Contacts',
            'companies': 'Companies',
            'leads': 'Leads',
            'deals': 'Deals',
            'tasks': 'Tasks',
            'projects': 'Projects',
            'memos': 'Memos'
        };
        return titles[section] || section.charAt(0).toUpperCase() + section.slice(1);
    }

    async loadSection(section) {
        const sectionElement = document.getElementById(`${section}-section`);

        switch (section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'contacts':
                if (this.isEndpointAvailable('contacts/')) {
                    this.loadContacts();
                } else {
                    this.showSectionNotAvailable(section, 'Contacts module not available in Django API');
                }
                break;
            case 'companies':
                if (this.isEndpointAvailable('companies/')) {
                    this.loadCompanies();
                } else {
                    this.showSectionNotAvailable(section, 'Companies module not available in Django API');
                }
                break;
            case 'leads':
                if (this.isEndpointAvailable('leads/')) {
                    this.loadLeads();
                } else {
                    this.showSectionNotAvailable(section, 'Leads module not available in Django API');
                }
                break;
            case 'deals':
                if (this.isEndpointAvailable('deals/')) {
                    this.loadDeals();
                } else {
                    this.showSectionNotAvailable(section, 'Deals module not available in Django API');
                }
                break;
            case 'tasks':
                if (this.isEndpointAvailable('tasks/')) {
                    this.loadTasks();
                } else {
                    this.showSectionNotAvailable(section, 'Tasks module not available in Django API');
                }
                break;
            case 'projects':
                if (this.isEndpointAvailable('projects/')) {
                    this.loadProjects();
                } else {
                    this.showSectionNotAvailable(section, 'Projects module not available in Django API');
                }
                break;
            case 'memos':
                if (this.isEndpointAvailable('memos/')) {
                    this.loadMemos();
                } else {
                    this.showSectionNotAvailable(section, 'Memos module not available in Django API');
                }
                break;
        }
    }

    isEndpointAvailable(endpoint) {
        return window.CRM_CONFIG.AVAILABLE_ENDPOINTS.includes(endpoint);
    }

    showSectionNotAvailable(section, message) {
        const sectionElement = document.getElementById(`${section}-section`);
        if (!sectionElement) return;

        sectionElement.innerHTML = `
            <div class="text-center py-16">
                <div class="max-w-md mx-auto">
                    <i class="fas fa-tools text-6xl text-gray-400 mb-6"></i>
                    <h3 class="text-xl font-semibold text-gray-900 mb-3">Module Under Development</h3>
                    <p class="text-gray-600 mb-6">${message}</p>

                    <div class="bg-primary bg-opacity-10 border border-primary border-opacity-20 rounded-lg p-4 mb-6">
                        <div class="flex items-center">
                            <i class="fas fa-info-circle text-primary mr-3"></i>
                            <div class="text-left">
                                <p class="text-primary font-medium">Available Sections:</p>
                                <p class="text-primary text-sm">Dashboard, ${window.CRM_CONFIG.AVAILABLE_ENDPOINTS.filter(ep =>
            ['contacts', 'companies', 'leads', 'deals', 'tasks'].some(module => ep.includes(module))
        ).map(ep => ep.split('/')[2]).join(', ')}</p>
                            </div>
                        </div>
                    </div>

                    <button data-action="switchSection" data-section="dashboard" 
                            class="bg-primary hover:bg-opacity-90 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-chart-line mr-2"></i>Go to Dashboard
                    </button>
                </div>
            </div>
        `;
    }

    // Handle API validation errors
    handleValidationError(error) {
        const { status, data } = error;

        if (status === 400 && data) {
            // Show validation error modal
            this.showValidationErrorModal(data);
        } else if (status === 401) {
            this.showToast('Authentication required. Please log in again.', 'error');
            this.handleAuthError();
        } else if (status === 403) {
            this.showToast('Access denied. You don\'t have permission to perform this action.', 'error');
        } else if (status === 404) {
            this.showToast('Resource not found.', 'error');
        } else if (status === 409) {
            this.showToast('Conflict: This resource already exists or is being used.', 'error');
        } else if (status >= 500) {
            this.showToast('Server error. Please try again later.', 'error');
        }
    }

    // Show detailed validation error modal
    showValidationErrorModal(errorData) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4';

        // Parse validation errors
        let errorMessages = [];

        if (errorData.details) {
            // Handle Django REST Framework style errors
            Object.entries(errorData.details).forEach(([field, messages]) => {
                if (Array.isArray(messages)) {
                    messages.forEach(message => {
                        errorMessages.push({
                            field: field === 'non_field_errors' ? 'General' : field,
                            message: message
                        });
                    });
                } else {
                    errorMessages.push({
                        field: field === 'non_field_errors' ? 'General' : field,
                        message: messages
                    });
                }
            });
        } else if (errorData.error) {
            errorMessages.push({
                field: 'General',
                message: errorData.error
            });
        } else if (errorData.message) {
            errorMessages.push({
                field: 'General',
                message: errorData.message
            });
        } else {
            errorMessages.push({
                field: 'General',
                message: 'Validation failed. Please check your input and try again.'
            });
        }

        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden">
                <div class="bg-danger bg-opacity-10 px-6 py-4 border-b border-danger border-opacity-20">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-triangle text-danger text-xl"></i>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-lg font-medium text-danger">Validation Error</h3>
                            <p class="text-danger text-sm mt-1">${errorData.error || 'Please correct the following errors:'}</p>
                        </div>
                    </div>
                </div>

                <div class="px-6 py-4">
                    <div class="space-y-3">
                        ${errorMessages.map(error => `
                            <div class="flex items-start space-x-3 p-3 bg-danger bg-opacity-10 rounded-lg border border-danger border-opacity-20">
                                <div class="flex-shrink-0 mt-0.5">
                                    <i class="fas fa-times-circle text-danger text-sm"></i>
                                </div>
                                <div class="min-w-0 flex-1">
                                    <p class="text-sm font-medium text-danger">${error.field}</p>
                                    <p class="text-sm text-danger mt-1">${error.message}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    ${errorData.help ? `
                        <div class="mt-4 p-3 bg-primary bg-opacity-10 rounded-lg border border-primary border-opacity-20">
                            <div class="flex">
                                <i class="fas fa-info-circle text-primary text-sm mt-0.5 mr-2"></i>
                                <p class="text-sm text-primary">${errorData.help}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()"
                            class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                        Close
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Auto-remove after 15 seconds
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 15000);
    }

    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto transition-all duration-300 transform translate-x-full`;

        const bgColor = type === 'success' ? 'bg-success bg-opacity-10 border-success border-opacity-20' :
            type === 'error' ? 'bg-danger bg-opacity-10 border-danger border-opacity-20' :
                type === 'warning' ? 'bg-warning bg-opacity-10 border-warning border-opacity-20' :
                    'bg-primary bg-opacity-10 border-primary border-opacity-20';

        const textColor = type === 'success' ? 'text-success' :
            type === 'error' ? 'text-danger' :
                type === 'warning' ? 'text-warning' :
                    'text-primary';

        const icon = type === 'success' ? 'fas fa-check-circle' :
            type === 'error' ? 'fas fa-times-circle' :
                type === 'warning' ? 'fas fa-exclamation-triangle' :
                    'fas fa-info-circle';

        toast.innerHTML = `
            <div class="p-4 ${bgColor} border rounded-lg">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <i class="${icon} ${textColor} text-lg"></i>
                    </div>
                    <div class="ml-3 flex-1">
                        <p class="text-sm ${textColor} font-medium">${message}</p>
                    </div>
                    <div class="ml-auto pl-3">
                        <button class="inline-flex ${textColor} hover:opacity-75 text-lg" onclick="this.closest('.max-w-sm').remove()">
                            <span class="sr-only">Close</span>
                            ✕
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('toast-container').appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Auto remove
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    }

    // Section loaders
    async loadDashboard() {
        const content = document.getElementById('dashboard-content');

        if (!this.token) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to Django CRM</h3>
                    <p class="text-gray-600 mb-4">Please log in to access your CRM data.</p>
                    <button onclick="app.showLoginModal()" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                        Log In
                    </button>
                </div>
            `;
            return;
        }

        // Show loading state
        content.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span class="ml-3 text-gray-600">Loading dashboard...</span>
            </div>
        `;

        try {
            // Use the new comprehensive dashboard data method
            const dashboardData = await window.apiClient.getDashboardData();
            const activityFeed = await window.apiClient.getActivityFeed(6);

            if (!dashboardData) {
                throw new Error('Failed to load dashboard data');
            }

            const { contacts, companies, deals, tasks, analytics, stats } = dashboardData;

            // Calculate deal pipeline value
            let pipelineValue = 0;
            if (deals && deals.length > 0) {
                pipelineValue = deals.reduce((sum, deal) => {
                    return sum + (parseFloat(deal.amount) || 0);
                }, 0);
            }

            // Format pipeline value
            const formatCurrency = (value) => {
                if (value >= 1000000) {
                    return `$${(value / 1000000).toFixed(1)}M`;
                } else if (value >= 1000) {
                    return `$${(value / 1000).toFixed(0)}K`;
                } else {
                    return `$${value.toFixed(0)}`;
                }
            };

            // Get growth indicators from analytics
            const contactsGrowth = analytics?.monthly_growth?.contacts || 0;
            const companiesGrowth = analytics?.monthly_growth?.companies || 0;
            const dealsGrowth = analytics?.monthly_growth?.deals || 0;
            const overdueTasks = analytics?.tasks?.overdue || 0;

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class=\"bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\" data-action=\"switchSection\" data-section=\"contacts\">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-primary bg-opacity-10 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-users text-primary text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Total Contacts</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${stats.contactsCount}</dd>
                                    <dd class="text-sm ${contactsGrowth > 0 ? 'text-success' : 'text-gray-500'}">
                                        ${contactsGrowth > 0 ? `+${contactsGrowth} this month` : 'No new this month'}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>

                    <div class=\"bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\" data-action=\"switchSection\" data-section=\"companies\">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-success bg-opacity-10 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-building text-success text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Total Companies</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${stats.companiesCount}</dd>
                                    <dd class="text-sm ${companiesGrowth > 0 ? 'text-success' : 'text-gray-500'}">
                                        ${companiesGrowth > 0 ? `+${companiesGrowth} this month` : 'No new this month'}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>

                    <div class=\"bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\" data-action=\"switchSection\" data-section=\"deals\">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-warning bg-opacity-10 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-handshake text-warning text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Active Deals</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${stats.dealsCount}</dd>
                                    <dd class="text-sm text-success">
                                        ${pipelineValue > 0 ? formatCurrency(pipelineValue) + ' pipeline' : 'No pipeline value'}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>

                    <div class=\"bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\" data-action=\"switchSection\" data-section=\"tasks\">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-danger bg-opacity-10 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-tasks text-danger text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Active Tasks</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${stats.tasksCount}</dd>
                                    <dd class="text-sm ${overdueTasks > 0 ? 'text-danger' : 'text-success'}">
                                        ${overdueTasks > 0 ? `${overdueTasks} overdue` : 'All up to date'}
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Recent Deals</h3>
                            <button data-action="switchSection" data-section="deals" class="text-primary hover:opacity-90 text-sm font-medium">
                                View all <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            ${deals && deals.length > 0 ? deals.slice(0, 4).map(deal => `
                                <div class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                                    <div class="w-2 h-2 bg-success rounded-full"></div>
                                    <div class="flex-1 min-w-0">
                                        <p class="font-medium text-gray-900 truncate">${deal.name || 'Unnamed Deal'}</p>
                                        <p class="text-sm text-gray-500">${deal.company_name || deal.company?.name || 'No company'}</p>
                                    </div>
                                    <div class="text-right">
                                        <p class="font-semibold text-gray-900">${deal.amount ? formatCurrency(parseFloat(deal.amount)) : '-'}</p>
                                        <p class="text-xs text-gray-500">${deal.stage_name || deal.stage?.name || 'No stage'}</p>
                                    </div>
                                </div>
                            `).join('') : '<div class="text-center py-8 text-gray-500">No deals found</div>'}
                        </div>
                    </div>

                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Recent Tasks</h3>
                            <button data-action="switchSection" data-section="tasks" class="text-primary hover:opacity-90 text-sm font-medium">
                                View all <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            ${tasks && tasks.length > 0 ? tasks.slice(0, 4).map(task => `
                                <div class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                                    <div class="w-4 h-4 border-2 border-gray-300 rounded flex items-center justify-center ${!task.active ? 'bg-success border-success' : ''}">
                                        ${!task.active ? '<i class="fas fa-check text-white text-xs"></i>' : ''}
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <p class="font-medium text-gray-900 truncate ${!task.active ? 'line-through text-gray-500' : ''}">${task.name || 'Unnamed Task'}</p>
                                        <p class="text-sm text-gray-500">${task.project_name || task.project?.name || 'No project'}</p>
                                    </div>
                                    <div class="text-right">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${task.active ? 'bg-warning bg-opacity-20 text-warning' : 'bg-success bg-opacity-20 text-success'}">
                                            ${task.active ? 'Active' : 'Done'}
                                        </span>
                                    </div>
                                </div>
                            `).join('') : '<div class="text-center py-8 text-gray-500">No tasks found</div>'}
                        </div>
                    </div>

                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Recent Activity</h3>
                            <button data-action="refreshDashboard" class="text-primary hover:opacity-90 text-sm font-medium">
                                <i class="fas fa-sync-alt mr-1"></i>Refresh
                            </button>
                        </div>
                        <div class="space-y-4">
                            ${activityFeed && activityFeed.length > 0 ? activityFeed.map(activity => {
                const timeAgo = this.formatTimeAgo(activity.timestamp);
                const colorClass = activity.color || 'primary';
                return `
                                    <div class="flex items-start space-x-3">
                                        <div class="w-8 h-8 bg-${colorClass} bg-opacity-10 rounded-full flex items-center justify-center">
                                            <i class="${activity.icon} text-${colorClass} text-xs"></i>
                                        </div>
                                        <div class="flex-1 min-w-0">
                                            <p class="text-sm text-gray-900">${activity.message}</p>
                                            <p class="text-xs text-gray-500">${timeAgo}</p>
                                        </div>
                                    </div>
                                `;
            }).join('') : `
                                <div class="text-center py-8 text-gray-500">
                                    <i class="fas fa-history text-2xl mb-2 text-gray-400"></i>
                                    <p>No recent activity</p>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading dashboard:', error);
            const errorMessage = error.message.includes('Network error')
                ? 'Cannot connect to the Django API server. Please make sure it\'s running on 127.0.0.1:8000'
                : 'Error loading dashboard data. Please try logging in again.';

            content.innerHTML = `
                <div class="bg-danger bg-opacity-10 border border-danger rounded-lg p-6">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-danger text-xl mr-3"></i>
                        <div>
                            <h3 class="text-lg font-medium text-danger">${'Dashboard Load Error'}</h3>
                            <p class="text-danger mt-1">${errorMessage}</p>
                            <button onclick="app.loadDashboard()" class="mt-3 bg-danger hover:bg-opacity-90 text-white px-4 py-2 rounded-lg text-sm">
                                Try Again
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    // Helper method to format timestamps
    formatTimeAgo(timestamp) {
        if (!timestamp) return 'Unknown time';

        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days > 1 ? 's' : ''} ago`;
        }
    }

    async loadContacts() {
        this.contacts.loadContacts();
    }

    async loadCompanies() {
        this.companies.loadCompanies();
    }

    async loadLeads() {
        this.leads.loadLeads();
    }

    async loadDeals() {
        this.deals.loadDeals();
    }

    async loadTasks() {
        this.tasks.loadTasks();
    }

    async loadProjects() {
        this.projects.loadProjects();
    }

    async loadMemos() {
        this.memos.loadMemos();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    window.app = new CRMApp();
});
