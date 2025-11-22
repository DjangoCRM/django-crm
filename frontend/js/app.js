// Django CRM Frontend Application
class CRMApp {
    constructor() {
        // Use configuration from config.js
        this.apiBase = window.CRM_CONFIG?.API_BASE_URL || 'http://127.0.0.1:8000/api';
        this.token = localStorage.getItem(window.CRM_CONFIG?.AUTH_TOKEN_KEY || 'crm_token');
        this.currentUser = null;
        this.currentSection = 'dashboard';
        
        // Debug info
        if (window.CRM_CONFIG?.DEBUG_MODE) {
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
        this.phone = new PhoneManager(this);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.loadSection('dashboard');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.switchSection(section);
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
    }

    async checkAuthStatus() {
        if (!this.token) {
            document.getElementById('auth-status').innerHTML = 
                '<span class="text-gray-500">Not logged in</span>';
            return;
        }

        try {
            const response = await this.apiCall('/users/me/');
            this.currentUser = response;
            document.getElementById('auth-status').innerHTML = 
                `<div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
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
            const [contacts, companies, leads, deals, tasks] = await Promise.all([
                this.apiCall('/contacts/?limit=1'),
                this.apiCall('/companies/?limit=1'),
                this.apiCall('/leads/?limit=1'),
                this.apiCall('/deals/?limit=1'),
                this.apiCall('/tasks/?limit=1')
            ]);

            document.getElementById('contacts-count').textContent = contacts.count || 0;
            document.getElementById('companies-count').textContent = companies.count || 0;
            document.getElementById('leads-count').textContent = leads.count || 0;
            document.getElementById('deals-count').textContent = deals.count || 0;
            document.getElementById('tasks-count').textContent = tasks.count || 0;
        } catch (error) {
            console.error('Error updating sidebar counts:', error);
        }
    }

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${this.apiBase}/auth/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                localStorage.setItem('crm_token', this.token);
                this.hideLoginModal();
                this.checkAuthStatus();
                this.loadSection(this.currentSection);
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
        
        this.loadSection('dashboard');
        this.showToast('Logged out successfully', 'success');
    }

    handleAuthError() {
        this.logout();
        this.showToast('Authentication expired. Please log in again.', 'error');
    }

    showLoginModal() {
        document.getElementById('login-modal').classList.remove('hidden');
    }

    hideLoginModal() {
        document.getElementById('login-modal').classList.add('hidden');
        document.getElementById('login-form').reset();
    }

    switchSection(section) {
        // Update navigation - new sidebar style
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('bg-primary-50', 'text-primary-700', 'border-primary-200');
            btn.classList.add('text-gray-700', 'hover:bg-gray-50');
            
            // Update icons
            const icon = btn.querySelector('i');
            if (icon) {
                icon.classList.remove('text-primary-600');
                icon.classList.add('text-gray-400');
            }
        });
        
        const activeBtn = document.querySelector(`[data-section="${section}"]`);
        if (activeBtn) {
            activeBtn.classList.remove('text-gray-700', 'hover:bg-gray-50');
            activeBtn.classList.add('bg-primary-50', 'text-primary-700', 'border', 'border-primary-200');
            
            // Update icon
            const icon = activeBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('text-gray-400');
                icon.classList.add('text-primary-600');
            }
        }

        // Update breadcrumb
        document.getElementById('current-section').textContent = this.getSectionTitle(section);

        // Show/hide sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.add('hidden');
            sec.classList.remove('active');
        });
        
        const targetSection = document.getElementById(`${section}-section`);
        targetSection.classList.remove('hidden');
        targetSection.classList.add('active');

        this.currentSection = section;
        this.loadSection(section);
    }

    getSectionTitle(section) {
        const titles = {
            'dashboard': 'Dashboard',
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
        
        switch(section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'contacts':
                this.loadContacts();
                break;
            case 'companies':
                this.loadCompanies();
                break;
            case 'leads':
                this.loadLeads();
                break;
            case 'deals':
                this.loadDeals();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'projects':
                this.loadProjects();
                break;
            case 'memos':
                this.loadMemos();
                break;
        }
    }

    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: window.CRM_CONFIG?.REQUEST_TIMEOUT || 30000
        };

        if (this.token) {
            defaultOptions.headers['Authorization'] = `Token ${this.token}`;
        }

        // Debug logging
        if (window.CRM_CONFIG?.DEBUG_MODE) {
            console.log(`🔄 API Call: ${options.method || 'GET'} ${url}`);
            if (options.body) {
                console.log('📤 Request Body:', options.body);
            }
        }

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            // Debug response
            if (window.CRM_CONFIG?.DEBUG_MODE) {
                console.log(`📥 Response: ${response.status} ${response.statusText}`);
            }
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            // Debug response data
            if (window.CRM_CONFIG?.DEBUG_MODE) {
                console.log('📦 Response Data:', data);
            }
            
            return data;
        } catch (error) {
            // Enhanced error handling
            if (window.CRM_CONFIG?.DEBUG_MODE) {
                console.error('❌ API Error:', error);
            }
            
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Network error: Cannot connect to Django API server. Is it running on 127.0.0.1:8000?');
            }
            
            throw error;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto transition-all duration-300 transform translate-x-full`;
        
        const bgColor = type === 'success' ? 'bg-green-50 border-green-200' : 
                       type === 'error' ? 'bg-red-50 border-red-200' : 
                       'bg-blue-50 border-blue-200';
        
        const textColor = type === 'success' ? 'text-green-800' : 
                         type === 'error' ? 'text-red-800' : 
                         'text-blue-800';

        toast.innerHTML = `
            <div class="p-4 ${bgColor} border rounded-lg">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <div class="w-5 h-5 ${textColor}">
                            ${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}
                        </div>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm ${textColor}">${message}</p>
                    </div>
                    <div class="ml-auto pl-3">
                        <button class="inline-flex ${textColor} hover:opacity-75" onclick="this.closest('.max-w-sm').remove()">
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

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // Section loaders
    async loadDashboard() {
        const content = document.getElementById('dashboard-content');
        if (!this.token) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to Django CRM</h3>
                    <p class="text-gray-600 mb-4">Please log in to access your CRM data.</p>
                    <button onclick="app.showLoginModal()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                        Log In
                    </button>
                </div>
            `;
            return;
        }

        try {
            const [contacts, companies, deals, tasks] = await Promise.all([
                this.apiCall('/contacts/?limit=5'),
                this.apiCall('/companies/?limit=5'),
                this.apiCall('/deals/?limit=5'),
                this.apiCall('/tasks/?limit=5')
            ]);

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer" onclick="app.switchSection('contacts')">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-users text-primary-600 text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Total Contacts</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${contacts.count || contacts.length}</dd>
                                    <dd class="text-sm text-success-600">+12% this month</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer" onclick="app.switchSection('companies')">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-building text-success-600 text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Total Companies</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${companies.count || companies.length}</dd>
                                    <dd class="text-sm text-success-600">+8% this month</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer" onclick="app.switchSection('deals')">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-handshake text-warning-600 text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Active Deals</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${deals.count || deals.length}</dd>
                                    <dd class="text-sm text-success-600">$2.4M pipeline</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer" onclick="app.switchSection('tasks')">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-tasks text-danger-600 text-xl"></i>
                                </div>
                            </div>
                            <div class="ml-4 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500">Pending Tasks</dt>
                                    <dd class="text-2xl font-bold text-gray-900">${tasks.count || tasks.length}</dd>
                                    <dd class="text-sm text-danger-600">3 overdue</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Recent Deals</h3>
                            <button onclick="app.switchSection('deals')" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                View all <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            ${deals.results ? deals.results.slice(0, 4).map(deal => `
                                <div class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                                    <div class="w-2 h-2 bg-success-500 rounded-full"></div>
                                    <div class="flex-1 min-w-0">
                                        <p class="font-medium text-gray-900 truncate">${deal.name}</p>
                                        <p class="text-sm text-gray-500">${deal.company_name || 'No company'}</p>
                                    </div>
                                    <div class="text-right">
                                        <p class="font-semibold text-gray-900">${deal.amount ? '$' + Math.round(deal.amount/1000) + 'K' : '-'}</p>
                                        <p class="text-xs text-gray-500">${deal.stage_name || 'No stage'}</p>
                                    </div>
                                </div>
                            `).join('') : '<div class="text-center py-8 text-gray-500">No deals found</div>'}
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Recent Tasks</h3>
                            <button onclick="app.switchSection('tasks')" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                View all <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            ${tasks.results ? tasks.results.slice(0, 4).map(task => `
                                <div class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                                    <div class="w-4 h-4 border-2 border-gray-300 rounded ${task.active ? '' : 'bg-success-500 border-success-500'}">
                                        ${task.active ? '' : '<i class="fas fa-check text-white text-xs"></i>'}
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <p class="font-medium text-gray-900 truncate ${task.active ? '' : 'line-through text-gray-500'}">${task.name}</p>
                                        <p class="text-sm text-gray-500">${task.project_name || 'No project'}</p>
                                    </div>
                                    <div class="text-right">
                                        <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${task.active ? 'bg-warning-100 text-warning-800' : 'bg-success-100 text-success-800'}">
                                            ${task.active ? 'Pending' : 'Done'}
                                        </span>
                                    </div>
                                </div>
                            `).join('') : '<div class="text-center py-8 text-gray-500">No tasks found</div>'}
                        </div>
                    </div>

                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Activity</h3>
                            <button class="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                View all <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            <div class="flex items-start space-x-3">
                                <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                                    <i class="fas fa-phone text-primary-600 text-xs"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm text-gray-900">Call completed with John Smith</p>
                                    <p class="text-xs text-gray-500">2 minutes ago</p>
                                </div>
                            </div>
                            <div class="flex items-start space-x-3">
                                <div class="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
                                    <i class="fas fa-handshake text-success-600 text-xs"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm text-gray-900">Deal "Enterprise Software" moved to Negotiation</p>
                                    <p class="text-xs text-gray-500">1 hour ago</p>
                                </div>
                            </div>
                            <div class="flex items-start space-x-3">
                                <div class="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center">
                                    <i class="fas fa-user-plus text-warning-600 text-xs"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm text-gray-900">New lead from website form</p>
                                    <p class="text-xs text-gray-500">3 hours ago</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading dashboard:', error);
            content.innerHTML = '<div class="text-red-600">Error loading dashboard data</div>';
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
document.addEventListener('DOMContentLoaded', function() {
    window.app = new CRMApp();
});