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
        this.analytics = new AnalyticsDashboard(this);
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
            'retry-load-dashboard': () => this.loadDashboard(),
            'retry-load-contacts': () => this.loadContacts(),
            'retry-load-companies': () => this.loadCompanies(),
            'retry-load-leads': () => this.loadLeads(),
            'retry-load-deals': () => this.loadDeals(),
            'retry-load-tasks': () => this.loadTasks(),
            'retry-load-projects': () => this.loadProjects(),
            'retry-load-memos': () => this.loadMemos(),
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

        // Restore focus after page load
        const focusedElementId = sessionStorage.getItem('crm_focused_element');
        if (focusedElementId) {
            sessionStorage.removeItem('crm_focused_element');
            // Use a timeout to ensure the element is visible and focusable after all rendering is done
            setTimeout(() => {
                const elementToFocus = document.getElementById(focusedElementId);
                if (elementToFocus) {
                    elementToFocus.focus();
                }
            }, 100);
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

        // Preserve focus across reloads
        window.addEventListener('beforeunload', () => {
            if (document.activeElement && document.activeElement.id) {
                sessionStorage.setItem('crm_focused_element', document.activeElement.id);
            }
        });
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
            const authStatusElement = document.getElementById('auth-status');
            authStatusElement.innerHTML = ''; // Clear existing content

            const userDiv = document.createElement('div');
            userDiv.className = 'flex items-center space-x-2';

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-sm font-medium';
            avatarDiv.textContent = `${(response.first_name || '').charAt(0)}${(response.last_name || '').charAt(0)}`;
            userDiv.appendChild(avatarDiv);

            const nameSpan = document.createElement('span');
            nameSpan.className = 'text-gray-700 font-medium';
            nameSpan.textContent = `${response.first_name} ${response.last_name}`;
            userDiv.appendChild(nameSpan);

            authStatusElement.appendChild(userDiv);

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
            'analytics': 'Analytics',
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
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }

    async loadAnalytics() {
        try {
            await this.analytics.render('analytics-content');
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showSectionLoadError('analytics');
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

    showSectionLoadError(section) {
        const sectionElement = document.getElementById(`${section}-section`);
        if (!sectionElement) return;

        sectionElement.innerHTML = `
            <div class="text-center py-16">
                <div class="max-w-md mx-auto">
                    <i class="fas fa-exclamation-triangle text-danger text-5xl mb-6"></i>
                    <h3 class="text-xl font-semibold text-gray-900 mb-3">Failed to Load Section</h3>
                    <p class="text-gray-600 mb-6">There was an unexpected error while loading this data. Please try again.</p>
                    <button data-action="retry-load-${section}" 
                            class="bg-primary hover:bg-opacity-90 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-sync-alt mr-2"></i>Retry
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

        const modalContent = document.createElement('div');
        modalContent.className = 'bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden';

        // Modal Header
        const headerDiv = document.createElement('div');
        headerDiv.className = 'bg-danger bg-opacity-10 px-6 py-4 border-b border-danger border-opacity-20';

        const headerFlex = document.createElement('div');
        headerFlex.className = 'flex items-center';

        const headerShrink = document.createElement('div');
        headerShrink.className = 'flex-shrink-0';
        const headerIcon = document.createElement('i');
        headerIcon.className = 'fas fa-exclamation-triangle text-danger text-xl';
        headerShrink.appendChild(headerIcon);
        headerFlex.appendChild(headerShrink);

        const headerMl3 = document.createElement('div');
        headerMl3.className = 'ml-3';
        const headerH3 = document.createElement('h3');
        headerH3.className = 'text-lg font-medium text-danger';
        headerH3.textContent = 'Validation Error';
        headerMl3.appendChild(headerH3);
        const headerP = document.createElement('p');
        headerP.className = 'text-danger text-sm mt-1';
        headerP.textContent = errorData.error || 'Please correct the following errors:'; // Use textContent
        headerMl3.appendChild(headerP);
        headerFlex.appendChild(headerMl3);
        headerDiv.appendChild(headerFlex);
        modalContent.appendChild(headerDiv);

        // Modal Body
        const bodyDiv = document.createElement('div');
        bodyDiv.className = 'px-6 py-4';

        const errorListDiv = document.createElement('div');
        errorListDiv.className = 'space-y-3';

        // Parse validation errors
        let errorMessages = [];
        if (errorData.details) {
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
            errorMessages.push({ field: 'General', message: errorData.error });
        } else if (errorData.message) {
            errorMessages.push({ field: 'General', message: errorData.message });
        } else {
            errorMessages.push({ field: 'General', message: 'Validation failed. Please check your input and try again.' });
        }

        errorMessages.forEach(error => {
            const errorItemDiv = document.createElement('div');
            errorItemDiv.className = 'flex items-start space-x-3 p-3 bg-danger bg-opacity-10 rounded-lg border border-danger border-opacity-20';

            const itemShrink = document.createElement('div');
            itemShrink.className = 'flex-shrink-0 mt-0.5';
            const itemIcon = document.createElement('i');
            itemIcon.className = 'fas fa-times-circle text-danger text-sm';
            itemShrink.appendChild(itemIcon);
            errorItemDiv.appendChild(itemShrink);

            const itemMinW = document.createElement('div');
            itemMinW.className = 'min-w-0 flex-1';
            const itemFieldP = document.createElement('p');
            itemFieldP.className = 'text-sm font-medium text-danger';
            itemFieldP.textContent = error.field; // Use textContent
            itemMinW.appendChild(itemFieldP);
            const itemMessageP = document.createElement('p');
            itemMessageP.className = 'text-sm text-danger mt-1';
            itemMessageP.textContent = error.message; // Use textContent
            itemMinW.appendChild(itemMessageP);
            errorItemDiv.appendChild(itemMinW);

            errorListDiv.appendChild(errorItemDiv);
        });
        bodyDiv.appendChild(errorListDiv);

        // Optional Help Text
        if (errorData.help) {
            const helpDiv = document.createElement('div');
            helpDiv.className = 'mt-4 p-3 bg-primary bg-opacity-10 rounded-lg border border-primary border-opacity-20';

            const helpFlex = document.createElement('div');
            helpFlex.className = 'flex';
            const helpIcon = document.createElement('i');
            helpIcon.className = 'fas fa-info-circle text-primary text-sm mt-0.5 mr-2';
            helpFlex.appendChild(helpIcon);
            const helpP = document.createElement('p');
            helpP.className = 'text-sm text-primary';
            helpP.textContent = errorData.help; // Use textContent
            helpFlex.appendChild(helpP);
            helpDiv.appendChild(helpFlex);
            bodyDiv.appendChild(helpDiv);
        }
        modalContent.appendChild(bodyDiv);

        // Modal Footer
        const footerDiv = document.createElement('div');
        footerDiv.className = 'bg-gray-50 px-6 py-4 flex justify-end space-x-3';

        const closeButton = document.createElement('button');
        closeButton.onclick = () => modal.remove();
        closeButton.className = 'bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors';
        closeButton.textContent = 'Close';
        footerDiv.appendChild(closeButton);
        modalContent.appendChild(footerDiv);

        modal.appendChild(modalContent);
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

        const p4Div = document.createElement('div');
        p4Div.className = `p-4 ${bgColor} border rounded-lg`;

        const flexDiv1 = document.createElement('div');
        flexDiv1.className = 'flex';

        const flexShrinkDiv = document.createElement('div');
        flexShrinkDiv.className = 'flex-shrink-0';
        const iElement = document.createElement('i');
        iElement.className = `${icon} ${textColor} text-lg`;
        flexShrinkDiv.appendChild(iElement);
        flexDiv1.appendChild(flexShrinkDiv);

        const ml3Div = document.createElement('div');
        ml3Div.className = 'ml-3 flex-1';
        const pElement = document.createElement('p');
        pElement.className = `text-sm ${textColor} font-medium`;
        pElement.textContent = message; // Set message via textContent
        ml3Div.appendChild(pElement);
        flexDiv1.appendChild(ml3Div);

        const mlAutoDiv = document.createElement('div');
        mlAutoDiv.className = 'ml-auto pl-3';
        const closeButton = document.createElement('button');
        closeButton.className = `inline-flex ${textColor} hover:opacity-75 text-lg`;
        closeButton.onclick = () => closeButton.closest('.max-w-sm').remove();
        const srOnlySpan = document.createElement('span');
        srOnlySpan.className = 'sr-only';
        srOnlySpan.textContent = 'Close';
        closeButton.appendChild(srOnlySpan);
        closeButton.append('✕');
        mlAutoDiv.appendChild(closeButton);
        flexDiv1.appendChild(mlAutoDiv);

        p4Div.appendChild(flexDiv1);
        toast.appendChild(p4Div);

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
        try {
            const content = document.getElementById('dashboard-content');

            if (!this.token) {
                content.innerHTML = ''; // Clear existing content
                const loginPromptDiv = document.createElement('div');
                loginPromptDiv.className = 'text-center py-8';

                const h3 = document.createElement('h3');
                h3.className = 'text-lg font-medium text-gray-900 mb-2';
                h3.textContent = 'Welcome to Django CRM';
                loginPromptDiv.appendChild(h3);

                const p = document.createElement('p');
                p.className = 'text-gray-600 mb-4';
                p.textContent = 'Please log in to access your CRM data.';
                loginPromptDiv.appendChild(p);

                const loginButton = document.createElement('button');
                loginButton.onclick = () => app.showLoginModal();
                loginButton.className = 'bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg';
                loginButton.textContent = 'Log In';
                loginPromptDiv.appendChild(loginButton);

                content.appendChild(loginPromptDiv);
                return;
            }

            // Show loading state
            content.innerHTML = ''; // Clear existing content
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'flex items-center justify-center py-8';
            const spinnerDiv = document.createElement('div');
            spinnerDiv.className = 'animate-spin rounded-full h-8 w-8 border-b-2 border-primary';
            loadingDiv.appendChild(spinnerDiv);
            const loadingSpan = document.createElement('span');
            loadingSpan.className = 'ml-3 text-gray-600';
            loadingSpan.textContent = 'Loading dashboard...';
            loadingDiv.appendChild(loadingSpan);
            content.appendChild(loadingDiv);

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

            content.innerHTML = ''; // Clear loading state

            const mainGrid = document.createElement('div');
            mainGrid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8';

            // Function to create a stat card
            const createStatCard = (section, iconClass, bgColorClass, title, count, growthText, growthIsPositive) => {
                const card = document.createElement('div');
                card.className = `bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700`;
                card.dataset.action = 'switchSection';
                card.dataset.section = section;

                const flexContainer = document.createElement('div');
                flexContainer.className = 'flex items-center';

                const iconShrink = document.createElement('div');
                iconShrink.className = 'flex-shrink-0';
                const iconDiv = document.createElement('div');
                iconDiv.className = `w-12 h-12 ${bgColorClass} bg-opacity-10 rounded-lg flex items-center justify-center`;
                const iconI = document.createElement('i');
                iconI.className = `${iconClass} ${bgColorClass} text-xl`;
                iconDiv.appendChild(iconI);
                iconShrink.appendChild(iconDiv);
                flexContainer.appendChild(iconShrink);

                const textMl4 = document.createElement('div');
                textMl4.className = 'ml-4 flex-1';
                const dl = document.createElement('dl');
                const dt = document.createElement('dt');
                dt.className = 'text-sm font-medium text-gray-500';
                dt.textContent = title;
                dl.appendChild(dt);
                const ddCount = document.createElement('dd');
                ddCount.className = 'text-2xl font-bold text-gray-900';
                ddCount.textContent = count;
                dl.appendChild(ddCount);
                const ddGrowth = document.createElement('dd');
                ddGrowth.className = `text-sm ${growthIsPositive ? 'text-success' : 'text-gray-500'}`;
                ddGrowth.textContent = growthText;
                dl.appendChild(ddGrowth);
                textMl4.appendChild(dl);
                flexContainer.appendChild(textMl4);
                card.appendChild(flexContainer);
                return card;
            };

            mainGrid.appendChild(createStatCard('contacts', 'fas fa-users', 'text-primary', 'Total Contacts', stats.contactsCount,
                contactsGrowth > 0 ? `+${contactsGrowth} this month` : 'No new this month', contactsGrowth > 0));
            mainGrid.appendChild(createStatCard('companies', 'fas fa-building', 'text-success', 'Total Companies', stats.companiesCount,
                companiesGrowth > 0 ? `+${companiesGrowth} this month` : 'No new this month', companiesGrowth > 0));
            mainGrid.appendChild(createStatCard('deals', 'fas fa-handshake', 'text-warning', 'Active Deals', stats.dealsCount,
                pipelineValue > 0 ? formatCurrency(pipelineValue) + ' pipeline' : 'No pipeline value', pipelineValue > 0));
            mainGrid.appendChild(createStatCard('tasks', 'fas fa-tasks', 'text-danger', 'Active Tasks', stats.tasksCount,
                overdueTasks > 0 ? `${overdueTasks} overdue` : 'All up to date', overdueTasks === 0));

            content.appendChild(mainGrid);

            const secondaryGrid = document.createElement('div');
            secondaryGrid.className = 'grid grid-cols-1 lg:grid-cols-3 gap-6';

            // Recent Deals card
            const recentDealsCard = document.createElement('div');
            recentDealsCard.className = 'bg-white rounded-lg border border-gray-200 p-6';
            const dealsHeader = document.createElement('div');
            dealsHeader.className = 'flex items-center justify-between mb-4';
            const dealsH3 = document.createElement('h3');
            dealsH3.className = 'text-lg font-semibold text-gray-900';
            dealsH3.textContent = 'Recent Deals';
            dealsHeader.appendChild(dealsH3);
            const dealsButton = document.createElement('button');
            dealsButton.dataset.action = 'switchSection';
            dealsButton.dataset.section = 'deals';
            dealsButton.className = 'text-primary hover:opacity-90 text-sm font-medium';
            dealsButton.innerHTML = `View all <i class="fas fa-arrow-right ml-1"></i>`; // Static HTML for icon
            dealsHeader.appendChild(dealsButton);
            recentDealsCard.appendChild(dealsHeader);

            const dealsSpaceY = document.createElement('div');
            dealsSpaceY.className = 'space-y-4';
            if (deals && deals.length > 0) {
                deals.slice(0, 4).forEach(deal => {
                    const dealItem = document.createElement('div');
                    dealItem.className = 'flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer';

                    const statusIndicator = document.createElement('div');
                    statusIndicator.className = 'w-2 h-2 bg-success rounded-full';
                    dealItem.appendChild(statusIndicator);

                    const flex1 = document.createElement('div');
                    flex1.className = 'flex-1 min-w-0';
                    const dealNameP = document.createElement('p');
                    dealNameP.className = 'font-medium text-gray-900 truncate';
                    dealNameP.textContent = deal.name || 'Unnamed Deal';
                    flex1.appendChild(dealNameP);
                    const companyNameP = document.createElement('p');
                    companyNameP.className = 'text-sm text-gray-500';
                    companyNameP.textContent = deal.company_name || deal.company?.name || 'No company';
                    flex1.appendChild(companyNameP);
                    dealItem.appendChild(flex1);

                    const textRight = document.createElement('div');
                    textRight.className = 'text-right';
                    const amountP = document.createElement('p');
                    amountP.className = 'font-semibold text-gray-900';
                    amountP.textContent = deal.amount ? formatCurrency(parseFloat(deal.amount)) : '-';
                    textRight.appendChild(amountP);
                    const stageP = document.createElement('p');
                    stageP.className = 'text-xs text-gray-500';
                    stageP.textContent = deal.stage_name || deal.stage?.name || 'No stage';
                    textRight.appendChild(stageP);
                    dealItem.appendChild(textRight);

                    dealsSpaceY.appendChild(dealItem);
                });
            } else {
                const noDealsDiv = document.createElement('div');
                noDealsDiv.className = 'text-center py-8 text-gray-500';
                noDealsDiv.textContent = 'No deals found';
                dealsSpaceY.appendChild(noDealsDiv);
            }
            recentDealsCard.appendChild(dealsSpaceY);
            secondaryGrid.appendChild(recentDealsCard);

            // Recent Tasks card
            const recentTasksCard = document.createElement('div');
            recentTasksCard.className = 'bg-white rounded-lg border border-gray-200 p-6';
            const tasksHeader = document.createElement('div');
            tasksHeader.className = 'flex items-center justify-between mb-4';
            const tasksH3 = document.createElement('h3');
            tasksH3.className = 'text-lg font-semibold text-gray-900';
            tasksH3.textContent = 'Recent Tasks';
            tasksHeader.appendChild(tasksH3);
            const tasksButton = document.createElement('button');
            tasksButton.dataset.action = 'switchSection';
            tasksButton.dataset.section = 'tasks';
            tasksButton.className = 'text-primary hover:opacity-90 text-sm font-medium';
            tasksButton.innerHTML = `View all <i class="fas fa-arrow-right ml-1"></i>`; // Static HTML for icon
            tasksHeader.appendChild(tasksButton);
            recentTasksCard.appendChild(tasksHeader);

            const tasksSpaceY = document.createElement('div');
            tasksSpaceY.className = 'space-y-4';
            if (tasks && tasks.length > 0) {
                tasks.slice(0, 4).forEach(task => {
                    const taskItem = document.createElement('div');
                    taskItem.className = 'flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer';

                    const checkboxDiv = document.createElement('div');
                    checkboxDiv.className = `w-4 h-4 border-2 border-gray-300 rounded flex items-center justify-center ${!task.active ? 'bg-success border-success' : ''}`;
                    if (!task.active) {
                        const checkIcon = document.createElement('i');
                        checkIcon.className = 'fas fa-check text-white text-xs';
                        checkboxDiv.appendChild(checkIcon);
                    }
                    taskItem.appendChild(checkboxDiv);

                    const flex1 = document.createElement('div');
                    flex1.className = 'flex-1 min-w-0';
                    const taskNameP = document.createElement('p');
                    taskNameP.className = `font-medium text-gray-900 truncate ${!task.active ? 'line-through text-gray-500' : ''}`;
                    taskNameP.textContent = task.name || 'Unnamed Task';
                    flex1.appendChild(taskNameP);
                    const projectNameP = document.createElement('p');
                    projectNameP.className = 'text-sm text-gray-500';
                    projectNameP.textContent = task.project_name || task.project?.name || 'No project';
                    flex1.appendChild(projectNameP);
                    taskItem.appendChild(flex1);

                    const textRight = document.createElement('div');
                    textRight.className = 'text-right';
                    const statusSpan = document.createElement('span');
                    statusSpan.className = `inline-flex px-2 py-1 text-xs font-medium rounded-full ${task.active ? 'bg-warning bg-opacity-20 text-warning' : 'bg-success bg-opacity-20 text-success'}`;
                    statusSpan.textContent = task.active ? 'Active' : 'Done';
                    textRight.appendChild(statusSpan);
                    taskItem.appendChild(textRight);

                    tasksSpaceY.appendChild(taskItem);
                });
            } else {
                const noTasksDiv = document.createElement('div');
                noTasksDiv.className = 'text-center py-8 text-gray-500';
                noTasksDiv.textContent = 'No tasks found';
                tasksSpaceY.appendChild(noTasksDiv);
            }
            recentTasksCard.appendChild(tasksSpaceY);
            secondaryGrid.appendChild(recentTasksCard);

            // Recent Activity card
            const recentActivityCard = document.createElement('div');
            recentActivityCard.className = 'bg-white rounded-lg border border-gray-200 p-6';
            const activityHeader = document.createElement('div');
            activityHeader.className = 'flex items-center justify-between mb-4';
            const activityH3 = document.createElement('h3');
            activityH3.className = 'text-lg font-semibold text-gray-900';
            activityH3.textContent = 'Recent Activity';
            activityHeader.appendChild(activityH3);
            const refreshButton = document.createElement('button');
            refreshButton.dataset.action = 'refreshDashboard';
            refreshButton.className = 'text-primary hover:opacity-90 text-sm font-medium';
            refreshButton.innerHTML = `<i class="fas fa-sync-alt mr-1"></i>Refresh`; // Static HTML for icon
            activityHeader.appendChild(refreshButton);
            recentActivityCard.appendChild(activityHeader);

            const activitySpaceY = document.createElement('div');
            activitySpaceY.className = 'space-y-4';
            if (activityFeed && activityFeed.length > 0) {
                activityFeed.forEach(activity => {
                    const timeAgo = this.formatTimeAgo(activity.timestamp);
                    const colorClass = activity.color || 'primary';

                    const activityItem = document.createElement('div');
                    activityItem.className = 'flex items-start space-x-3';

                    const iconDiv = document.createElement('div');
                    iconDiv.className = `w-8 h-8 bg-${colorClass} bg-opacity-10 rounded-full flex items-center justify-center`;
                    const iconI = document.createElement('i');
                    iconI.className = `${activity.icon} text-${colorClass} text-xs`;
                    iconDiv.appendChild(iconI);
                    activityItem.appendChild(iconDiv);

                    const textContentDiv = document.createElement('div');
                    textContentDiv.className = 'flex-1 min-w-0';
                    const messageP = document.createElement('p');
                    messageP.className = 'text-sm text-gray-900';
                    messageP.textContent = activity.message; // Use textContent
                    textContentDiv.appendChild(messageP);
                    const timeP = document.createElement('p');
                    timeP.className = 'text-xs text-gray-500';
                    timeP.textContent = timeAgo; // Use textContent
                    textContentDiv.appendChild(timeP);
                    activityItem.appendChild(textContentDiv);

                    activitySpaceY.appendChild(activityItem);
                });
            } else {
                const noActivityDiv = document.createElement('div');
                noActivityDiv.className = 'text-center py-8 text-gray-500';
                const historyIcon = document.createElement('i');
                historyIcon.className = 'fas fa-history text-2xl mb-2 text-gray-400';
                noActivityDiv.appendChild(historyIcon);
                const noActivityP = document.createElement('p');
                noActivityP.textContent = 'No recent activity';
                noActivityDiv.appendChild(noActivityP);
                activitySpaceY.appendChild(noActivityDiv);
            }
            recentActivityCard.appendChild(activitySpaceY);
            secondaryGrid.appendChild(recentActivityCard);

            content.appendChild(secondaryGrid);

        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showSectionLoadError('dashboard');
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
        try {
            await this.contacts.loadContacts();
        } catch (error) {
            console.error(`Error loading contacts section:`, error);
            this.showSectionLoadError('contacts');
        }
    }

    async loadCompanies() {
        try {
            await this.companies.loadCompanies();
        } catch (error) {
            console.error(`Error loading companies section:`, error);
            this.showSectionLoadError('companies');
        }
    }

    async loadLeads() {
        try {
            await this.leads.loadLeads();
        } catch (error) {
            console.error(`Error loading leads section:`, error);
            this.showSectionLoadError('leads');
        }
    }

    async loadDeals() {
        try {
            await this.deals.loadDeals();
        } catch (error) {
            console.error(`Error loading deals section:`, error);
            this.showSectionLoadError('deals');
        }
    }

    async loadTasks() {
        try {
            await this.tasks.loadTasks();
        } catch (error) {
            console.error(`Error loading tasks section:`, error);
            this.showSectionLoadError('tasks');
        }
    }

    async loadProjects() {
        try {
            await this.projects.loadProjects();
        } catch (error) {
            console.error(`Error loading projects section:`, error);
            this.showSectionLoadError('projects');
        }
    }

    async loadMemos() {
        try {
            await this.memos.loadMemos();
        } catch (error) {
            console.error(`Error loading memos section:`, error);
            this.showSectionLoadError('memos');
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    window.app = new CRMApp();
});
