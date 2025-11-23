/**
 * Enhanced Lead Management with Modern UX/UI Practices
 * Provides advanced functionality for lead management including:
 * - Skeleton loading states
 * - Advanced filtering and sorting
 * - Keyboard shortcuts
 * - Drag and drop
 * - Real-time search
 * - Progressive disclosure
 * - Smart defaults
 * - Accessibility features
 */

class EnhancedLeadManager extends LeadManager {
    constructor(app) {
        super(app);
        this.currentView = 'cards'; // cards, table, kanban
        this.filters = new Map();
        this.sortConfig = { field: 'creation_date', direction: 'desc' };
        this.selectedLeads = new Set();
        this.searchTerm = '';
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalCount = 0;
        
        // Initialize advanced features
        this.initializeKeyboardShortcuts();
        this.initializeRealTimeSearch();
    }

    /**
     * Initialize keyboard shortcuts for power users
     */
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only process shortcuts when not in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            // Prevent default for our shortcuts
            const shortcuts = ['KeyN', 'KeyF', 'KeyS', 'Escape', 'KeyA'];
            if (e.ctrlKey || e.metaKey) {
                if (shortcuts.includes(e.code)) e.preventDefault();
            }
            
            switch (true) {
                case (e.ctrlKey || e.metaKey) && e.code === 'KeyN':
                    this.showLeadForm();
                    break;
                case (e.ctrlKey || e.metaKey) && e.code === 'KeyF':
                    document.getElementById('lead-search')?.focus();
                    break;
                case (e.ctrlKey || e.metaKey) && e.code === 'KeyS':
                    this.exportLeads();
                    break;
                case (e.ctrlKey || e.metaKey) && e.code === 'KeyA':
                    this.selectAllLeads();
                    break;
                case e.code === 'Escape':
                    this.clearSelection();
                    document.querySelector('.modal-overlay')?.remove();
                    break;
            }
        });
    }

    /**
     * Initialize real-time search with advanced debouncing
     */
    initializeRealTimeSearch() {
        let searchTimeout;
        let lastSearchTerm = '';
        
        this.searchHandler = (term) => {
            clearTimeout(searchTimeout);
            
            // Immediate search for short terms or when clearing
            if (term.length <= 2 || term === '') {
                this.performSearch(term);
                return;
            }
            
            // Debounced search for longer terms
            searchTimeout = setTimeout(() => {
                if (term !== lastSearchTerm) {
                    this.performSearch(term);
                    lastSearchTerm = term;
                }
            }, 300);
        };
    }

    /**
     * Enhanced loadLeads with modern UI patterns
     */
    async loadLeads() {
        this.selected = new Set();
        const section = document.getElementById('leads-section');
        
        section.innerHTML = `
            <div class="enhanced-leads-container">
                <!-- Header with Actions -->
                <div class="leads-header bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                            <div class="flex items-center space-x-4">
                                <h1 class="text-2xl font-bold text-gray-900 flex items-center">
                                    <span class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                                        🎯
                                    </span>
                                    Leads
                                </h1>
                                <div class="text-sm text-gray-500" id="leads-count">
                                    Loading...
                                </div>
                            </div>
                            
                            <!-- Actions -->
                            <div class="flex items-center space-x-3">
                                <button onclick="app.leads.showLeadForm()" 
                                        class="btn-primary flex items-center space-x-2"
                                        title="Create new lead (Ctrl+N)">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                                    </svg>
                                    <span>Add Lead</span>
                                </button>
                                
                                <div class="relative" id="view-switcher">
                                    <select class="input-select" onchange="app.leads.switchView(this.value)">
                                        <option value="cards">Cards View</option>
                                        <option value="table">Table View</option>
                                        <option value="kanban">Kanban View</option>
                                    </select>
                                </div>
                                
                                <button onclick="app.leads.toggleFilters()" 
                                        class="btn-secondary flex items-center space-x-2"
                                        title="Toggle filters (Ctrl+F)">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                                    </svg>
                                    <span>Filter</span>
                                </button>
                                
                                <div class="dropdown">
                                    <button class="btn-secondary dropdown-trigger flex items-center space-x-2">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
                                        </svg>
                                        <span>More</span>
                                    </button>
                                    <div class="dropdown-menu">
                                        <button onclick="app.leads.exportLeads()" class="dropdown-item">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                                            </svg>
                                            Export Leads
                                        </button>
                                        <button onclick="app.leads.showImportDialog()" class="dropdown-item">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
                                            </svg>
                                            Import Leads
                                        </button>
                                        <div class="dropdown-divider"></div>
                                        <button onclick="app.leads.showSettings()" class="dropdown-item">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                            </svg>
                                            Settings
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Search and Quick Filters -->
                    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
                        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                            <!-- Search -->
                            <div class="flex-1 max-w-md">
                                <div class="relative">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                                        </svg>
                                    </div>
                                    <input type="text" 
                                           id="lead-search" 
                                           class="input-search pl-10" 
                                           placeholder="Search leads... (Ctrl+F)"
                                           autocomplete="off">
                                    <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                                        <div id="search-spinner" class="hidden">
                                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Quick Filters -->
                            <div class="flex items-center space-x-3">
                                <select id="status-filter" class="input-select-sm" onchange="app.leads.applyQuickFilter('status', this.value)">
                                    <option value="">All Status</option>
                                    <option value="active">Active</option>
                                    <option value="contacted">Contacted</option>
                                    <option value="qualified">Qualified</option>
                                    <option value="disqualified">Disqualified</option>
                                </select>
                                
                                <select id="source-filter" class="input-select-sm" onchange="app.leads.applyQuickFilter('source', this.value)">
                                    <option value="">All Sources</option>
                                    <!-- Will be populated dynamically -->
                                </select>
                                
                                <select id="owner-filter" class="input-select-sm" onchange="app.leads.applyQuickFilter('owner', this.value)">
                                    <option value="">All Owners</option>
                                    <option value="me">My Leads</option>
                                    <!-- Will be populated dynamically -->
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Filters (Hidden by default) -->
                <div id="advanced-filters" class="hidden bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
                    <div class="px-6 py-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Advanced Filters</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <!-- Date Range -->
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Created Date</label>
                                <div class="grid grid-cols-2 gap-2">
                                    <input type="date" id="date-from" class="input-sm" placeholder="From">
                                    <input type="date" id="date-to" class="input-sm" placeholder="To">
                                </div>
                            </div>
                            
                            <!-- Industry -->
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Industry</label>
                                <select id="industry-filter" class="input-select-sm" multiple>
                                    <!-- Will be populated dynamically -->
                                </select>
                            </div>
                            
                            <!-- Location -->
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Location</label>
                                <input type="text" id="location-filter" class="input-sm" placeholder="City, Country">
                            </div>
                            
                            <!-- Tags -->
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Tags</label>
                                <div id="tags-filter" class="tags-input">
                                    <!-- Will be populated dynamically -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4 flex items-center justify-between">
                            <button onclick="app.leads.clearAllFilters()" class="btn-secondary-sm">
                                Clear All Filters
                            </button>
                            <div class="flex items-center space-x-2">
                                <button onclick="app.leads.saveFilterPreset()" class="btn-secondary-sm">
                                    Save Preset
                                </button>
                                <button onclick="app.leads.applyAdvancedFilters()" class="btn-primary-sm">
                                    Apply Filters
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Bulk Actions Bar (Hidden by default) -->
                <div id="bulk-actions-bar" class="hidden bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <span class="text-sm font-medium text-blue-900">
                                <span id="selected-count">0</span> leads selected
                            </span>
                            <button onclick="app.leads.selectAll()" class="text-sm text-blue-600 hover:text-blue-800">
                                Select all <span id="total-count">0</span> leads
                            </button>
                            <button onclick="app.leads.clearSelection()" class="text-sm text-blue-600 hover:text-blue-800">
                                Clear selection
                            </button>
                        </div>
                        
                        <div class="flex items-center space-x-2">
                            <button onclick="app.leads.bulkAssign()" class="btn-primary-sm">
                                Assign Owner
                            </button>
                            <button onclick="app.leads.bulkTag()" class="btn-secondary-sm">
                                Add Tags
                            </button>
                            <button onclick="app.leads.bulkUpdateStatus()" class="btn-secondary-sm">
                                Update Status
                            </button>
                            <button onclick="app.leads.bulkExport()" class="btn-secondary-sm">
                                Export Selected
                            </button>
                            <div class="h-4 w-px bg-gray-300"></div>
                            <button onclick="app.leads.bulkDelete()" class="btn-danger-sm">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Main Content Area -->
                <div id="leads-content" class="bg-white rounded-lg shadow-sm border border-gray-200">
                    <!-- Content will be loaded here -->
                </div>
                
                <!-- Pagination -->
                <div id="leads-pagination" class="hidden mt-6 flex items-center justify-between">
                    <div class="flex items-center space-x-2 text-sm text-gray-500">
                        <span>Show</span>
                        <select id="page-size-select" class="input-select-sm" onchange="app.leads.changePageSize(this.value)">
                            <option value="10">10</option>
                            <option value="20" selected>20</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                        </select>
                        <span>per page</span>
                    </div>
                    
                    <div class="flex items-center space-x-2">
                        <button id="prev-page" onclick="app.leads.previousPage()" class="btn-secondary-sm" disabled>
                            Previous
                        </button>
                        <div id="page-numbers" class="flex items-center space-x-1">
                            <!-- Page numbers will be generated here -->
                        </div>
                        <button id="next-page" onclick="app.leads.nextPage()" class="btn-secondary-sm" disabled>
                            Next
                        </button>
                    </div>
                    
                    <div class="text-sm text-gray-500">
                        Showing <span id="showing-from">1</span> to <span id="showing-to">20</span> of <span id="showing-total">0</span> results
                    </div>
                </div>
            </div>
        `;

        // Initialize event handlers
        this.setupEventHandlers();
        
        // Load initial data
        if (this.app.token) {
            await this.loadLeadsList();
            await this.loadFilterOptions();
        }
    }

    /**
     * Setup all event handlers for the enhanced interface
     */
    setupEventHandlers() {
        // Search functionality
        const searchInput = document.getElementById('lead-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchHandler(e.target.value);
            });
            
            // Clear search on Escape
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    e.target.value = '';
                    this.searchHandler('');
                }
            });
        }
        
        // Dropdown toggles
        this.setupDropdowns();
        
        // Advanced filters toggle
        const filterBtn = document.querySelector('[onclick="app.leads.toggleFilters()"]');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.toggleFilters());
        }
    }

    /**
     * Setup dropdown functionality
     */
    setupDropdowns() {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            const trigger = dropdown.querySelector('.dropdown-trigger');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (trigger && menu) {
                trigger.addEventListener('click', (e) => {
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(other => {
                        if (other !== menu) other.classList.remove('show');
                    });
                    
                    menu.classList.toggle('show');
                });
            }
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        });
    }

    /**
     * Enhanced loadLeadsList with skeleton loading and pagination
     */
    async loadLeadsList() {
        const content = document.getElementById('leads-content');
        
        // Show skeleton loading
        this.showSkeletonLoader(content);
        
        try {
            // Build API URL with filters and pagination
            const url = this.buildAPIURL();
            
            const response = await window.apiClient.get(url);
            this.totalCount = response.count || 0;
            
            // Update counts
            this.updateCounts(response.count || 0);
            
            // Render based on current view
            switch (this.currentView) {
                case 'table':
                    this.renderTableView(content, response.results || []);
                    break;
                case 'kanban':
                    this.renderKanbanView(content, response.results || []);
                    break;
                default:
                    this.renderCardsView(content, response.results || []);
            }
            
            // Update pagination
            this.updatePagination(response.count || 0);
            
            // Setup bulk selection if there are leads
            if (response.results && response.results.length > 0) {
                this.setupBulkSelection();
            }
            
        } catch (error) {
            this.showErrorState(content, error);
        }
    }

    /**
     * Show skeleton loader while content is loading
     */
    showSkeletonLoader(container) {
        if (this.currentView === 'table') {
            container.innerHTML = `
                <div class="overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                        <div class="flex items-center space-x-4">
                            <div class="skeleton skeleton-checkbox"></div>
                            <div class="skeleton skeleton-text w-24"></div>
                            <div class="skeleton skeleton-text w-32"></div>
                            <div class="skeleton skeleton-text w-28"></div>
                            <div class="skeleton skeleton-text w-20"></div>
                            <div class="skeleton skeleton-text w-24"></div>
                        </div>
                    </div>
                    ${Array(8).fill().map(() => `
                        <div class="px-6 py-4 border-b border-gray-100">
                            <div class="flex items-center space-x-4">
                                <div class="skeleton skeleton-checkbox"></div>
                                <div class="flex items-center space-x-3">
                                    <div class="skeleton skeleton-avatar"></div>
                                    <div>
                                        <div class="skeleton skeleton-text w-32 mb-1"></div>
                                        <div class="skeleton skeleton-text w-24"></div>
                                    </div>
                                </div>
                                <div class="skeleton skeleton-text w-28"></div>
                                <div class="skeleton skeleton-text w-36"></div>
                                <div class="skeleton skeleton-badge"></div>
                                <div class="skeleton skeleton-text w-20"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${Array(9).fill().map(() => `
                            <div class="bg-white border border-gray-200 rounded-lg p-6">
                                <div class="flex items-start space-x-4 mb-4">
                                    <div class="skeleton skeleton-checkbox"></div>
                                    <div class="skeleton skeleton-avatar"></div>
                                    <div class="flex-1">
                                        <div class="skeleton skeleton-text w-32 mb-2"></div>
                                        <div class="skeleton skeleton-text w-24"></div>
                                    </div>
                                    <div class="skeleton skeleton-badge"></div>
                                </div>
                                <div class="space-y-3">
                                    <div class="skeleton skeleton-text w-full"></div>
                                    <div class="skeleton skeleton-text w-3/4"></div>
                                    <div class="skeleton skeleton-text w-1/2"></div>
                                </div>
                                <div class="flex space-x-2 mt-4 pt-4 border-t border-gray-200">
                                    <div class="skeleton skeleton-button"></div>
                                    <div class="skeleton skeleton-button"></div>
                                    <div class="skeleton skeleton-button"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    /**
     * Build API URL with current filters, search, and pagination
     */
    buildAPIURL() {
        const params = new URLSearchParams();
        
        // Search
        if (this.searchTerm) {
            params.append('search', this.searchTerm);
        }
        
        // Filters
        this.filters.forEach((value, key) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });
        
        // Sorting
        if (this.sortConfig.field) {
            const sortParam = this.sortConfig.direction === 'desc' 
                ? `-${this.sortConfig.field}` 
                : this.sortConfig.field;
            params.append('ordering', sortParam);
        }
        
        // Pagination
        params.append('limit', this.pageSize.toString());
        params.append('offset', ((this.currentPage - 1) * this.pageSize).toString());
        
        return `${window.CRM_CONFIG.ENDPOINTS.LEADS}?${params.toString()}`;
    }

    // ... continuing with more methods
}

    /**
     * Render cards view with enhanced features
     */
    renderCardsView(container, leads) {
        if (leads.length === 0) {
            this.showEmptyState(container);
            return;
        }

        container.innerHTML = `
            <div class="p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    ${leads.map(lead => this.renderLeadCard(lead)).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render enhanced lead card
     */
    renderLeadCard(lead) {
        const statusColor = this.getStatusColor(lead);
        const priorityIcon = this.getPriorityIcon(lead.priority);
        
        return `
            <div class="lead-card group relative bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all duration-200 cursor-pointer"
                 data-lead-id="${lead.id}"
                 onclick="app.leads.viewLead(${lead.id})">
                
                <!-- Selection Checkbox -->
                <div class="absolute top-4 left-4">
                    <input type="checkbox" 
                           class="lead-checkbox rounded" 
                           value="${lead.id}"
                           onclick="event.stopPropagation(); app.leads.toggleLeadSelection(${lead.id})"
                           data-lead-id="${lead.id}">
                </div>
                
                <!-- Priority Indicator -->
                ${lead.priority ? `
                    <div class="absolute top-4 right-4">
                        <span class="priority-indicator" title="Priority: ${lead.priority}">
                            ${priorityIcon}
                        </span>
                    </div>
                ` : ''}
                
                <!-- Header -->
                <div class="flex items-start space-x-4 mb-4 pt-6">
                    <div class="lead-avatar">
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br ${this.getGradientColors(lead)} flex items-center justify-center text-white font-semibold text-lg">
                            ${this.getInitials(lead.first_name, lead.last_name)}
                        </div>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                        <h3 class="text-lg font-semibold text-gray-900 truncate">
                            ${lead.full_name || 'Unnamed Lead'}
                        </h3>
                        <p class="text-sm text-gray-500 truncate">
                            ${lead.company_name || lead.title || 'No company'}
                        </p>
                    </div>
                    
                    <div class="status-badge">
                        <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColor}">
                            ${this.getStatusText(lead)}
                        </span>
                    </div>
                </div>
                
                <!-- Contact Info -->
                <div class="space-y-2 mb-4">
                    ${lead.email ? `
                        <div class="flex items-center text-sm text-gray-600">
                            <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                            <span class="truncate">${lead.email}</span>
                        </div>
                    ` : ''}
                    
                    ${lead.phone ? `
                        <div class="flex items-center text-sm text-gray-600">
                            <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                            </svg>
                            <span class="truncate">${lead.phone}</span>
                        </div>
                    ` : ''}
                    
                    ${lead.city_name || lead.country ? `
                        <div class="flex items-center text-sm text-gray-600">
                            <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            <span class="truncate">${[lead.city_name, lead.country].filter(Boolean).join(', ')}</span>
                        </div>
                    ` : ''}
                </div>
                
                <!-- Lead Source -->
                ${lead.lead_source ? `
                    <div class="mb-4">
                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                            </svg>
                            ${lead.lead_source}
                        </span>
                    </div>
                ` : ''}
                
                <!-- Tags -->
                ${lead.tags && lead.tags.length > 0 ? `
                    <div class="mb-4">
                        <div class="flex flex-wrap gap-1">
                            ${lead.tags.slice(0, 3).map(tag => `
                                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                                    #${tag.name || tag}
                                </span>
                            `).join('')}
                            ${lead.tags.length > 3 ? `
                                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-500">
                                    +${lead.tags.length - 3}
                                </span>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Quick Actions -->
                <div class="flex items-center justify-between pt-4 border-t border-gray-200">
                    <div class="flex items-center space-x-1 text-xs text-gray-500">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span>${this.formatRelativeTime(lead.creation_date)}</span>
                    </div>
                    
                    <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onclick="event.stopPropagation(); app.leads.quickCall(${lead.id})"
                                class="p-1 rounded-md hover:bg-gray-100 text-gray-400 hover:text-blue-500"
                                title="Call">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                            </svg>
                        </button>
                        
                        <button onclick="event.stopPropagation(); app.leads.quickEmail(${lead.id})"
                                class="p-1 rounded-md hover:bg-gray-100 text-gray-400 hover:text-green-500"
                                title="Email">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                        </button>
                        
                        <button onclick="event.stopPropagation(); app.leads.editLead(${lead.id})"
                                class="p-1 rounded-md hover:bg-gray-100 text-gray-400 hover:text-yellow-500"
                                title="Edit">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </button>
                        
                        ${!lead.disqualified ? `
                            <button onclick="event.stopPropagation(); app.leads.convertLead(${lead.id})"
                                    class="p-1 rounded-md hover:bg-gray-100 text-gray-400 hover:text-green-600"
                                    title="Convert">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
                                </svg>
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render table view with sortable columns
     */
    renderTableView(container, leads) {
        if (leads.length === 0) {
            this.showEmptyState(container);
            return;
        }

        container.innerHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left">
                                <input type="checkbox" id="select-all-leads" class="rounded">
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onclick="app.leads.sortBy('full_name')">
                                <div class="flex items-center space-x-1">
                                    <span>Lead</span>
                                    ${this.getSortIcon('full_name')}
                                </div>
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onclick="app.leads.sortBy('company_name')">
                                <div class="flex items-center space-x-1">
                                    <span>Company</span>
                                    ${this.getSortIcon('company_name')}
                                </div>
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Contact
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onclick="app.leads.sortBy('status')">
                                <div class="flex items-center space-x-1">
                                    <span>Status</span>
                                    ${this.getSortIcon('status')}
                                </div>
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onclick="app.leads.sortBy('lead_source')">
                                <div class="flex items-center space-x-1">
                                    <span>Source</span>
                                    ${this.getSortIcon('lead_source')}
                                </div>
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onclick="app.leads.sortBy('creation_date')">
                                <div class="flex items-center space-x-1">
                                    <span>Created</span>
                                    ${this.getSortIcon('creation_date')}
                                </div>
                            </th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${leads.map(lead => this.renderTableRow(lead)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Setup select all functionality
        this.setupSelectAll();
    }

    /**
     * Render table row for a lead
     */
    renderTableRow(lead) {
        const statusColor = this.getStatusColor(lead);
        
        return `
            <tr class="hover:bg-gray-50 transition-colors" data-lead-id="${lead.id}">
                <td class="px-6 py-4">
                    <input type="checkbox" 
                           class="lead-checkbox rounded" 
                           value="${lead.id}"
                           data-lead-id="${lead.id}">
                </td>
                
                <td class="px-6 py-4">
                    <div class="flex items-center cursor-pointer" onclick="app.leads.viewLead(${lead.id})">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gradient-to-br ${this.getGradientColors(lead)} flex items-center justify-center text-white font-medium">
                                ${this.getInitials(lead.first_name, lead.last_name)}
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${lead.full_name || 'Unnamed Lead'}</div>
                            <div class="text-sm text-gray-500">${lead.title || ''}</div>
                        </div>
                    </div>
                </td>
                
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${lead.company_name || '-'}</div>
                </td>
                
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${lead.email || '-'}</div>
                    ${lead.phone ? `<div class="text-sm text-gray-500">${lead.phone}</div>` : ''}
                </td>
                
                <td class="px-6 py-4">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColor}">
                        ${this.getStatusText(lead)}
                    </span>
                </td>
                
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${lead.lead_source || '-'}</div>
                </td>
                
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">${this.formatDate(lead.creation_date)}</div>
                    <div class="text-xs text-gray-500">${this.formatRelativeTime(lead.creation_date)}</div>
                </td>
                
                <td class="px-6 py-4 text-right">
                    <div class="flex justify-end space-x-2">
                        <button onclick="app.leads.quickCall(${lead.id})" 
                                class="text-blue-600 hover:text-blue-800 text-sm"
                                title="Call">
                            Call
                        </button>
                        <button onclick="app.leads.editLead(${lead.id})" 
                                class="text-indigo-600 hover:text-indigo-800 text-sm">
                            Edit
                        </button>
                        ${!lead.disqualified ? `
                            <button onclick="app.leads.convertLead(${lead.id})" 
                                    class="text-green-600 hover:text-green-800 text-sm">
                                Convert
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * Render Kanban view with drag and drop
     */
    renderKanbanView(container, leads) {
        const statuses = ['new', 'contacted', 'qualified', 'unqualified'];
        const groupedLeads = this.groupLeadsByStatus(leads);

        container.innerHTML = `
            <div class="kanban-board p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    ${statuses.map(status => `
                        <div class="kanban-column" data-status="${status}">
                            <div class="kanban-header bg-gray-50 rounded-t-lg p-4 border-b border-gray-200">
                                <div class="flex items-center justify-between">
                                    <h3 class="font-semibold text-gray-900 capitalize">${status}</h3>
                                    <span class="bg-gray-200 text-gray-700 text-sm px-2 py-1 rounded-full">
                                        ${(groupedLeads[status] || []).length}
                                    </span>
                                </div>
                            </div>
                            
                            <div class="kanban-cards min-h-96 bg-gray-50 rounded-b-lg p-4 space-y-3" 
                                 data-status="${status}"
                                 ondrop="app.leads.handleDrop(event)" 
                                 ondragover="app.leads.handleDragOver(event)">
                                ${(groupedLeads[status] || []).map(lead => this.renderKanbanCard(lead)).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Setup drag and drop
        this.setupDragAndDrop();
    }

    /**
     * Render Kanban card for drag and drop
     */
    renderKanbanCard(lead) {
        return `
            <div class="kanban-card bg-white border border-gray-200 rounded-lg p-4 cursor-move"
                 draggable="true"
                 data-lead-id="${lead.id}"
                 ondragstart="app.leads.handleDragStart(event)"
                 onclick="app.leads.viewLead(${lead.id})">
                
                <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <input type="checkbox" 
                               class="lead-checkbox rounded" 
                               value="${lead.id}"
                               onclick="event.stopPropagation()"
                               data-lead-id="${lead.id}">
                        <div class="w-8 h-8 rounded-full bg-gradient-to-br ${this.getGradientColors(lead)} flex items-center justify-center text-white font-medium text-sm">
                            ${this.getInitials(lead.first_name, lead.last_name)}
                        </div>
                    </div>
                    
                    <div class="text-xs text-gray-500">
                        ${this.formatRelativeTime(lead.creation_date)}
                    </div>
                </div>
                
                <h4 class="font-medium text-gray-900 mb-1">${lead.full_name || 'Unnamed Lead'}</h4>
                <p class="text-sm text-gray-600 mb-3">${lead.company_name || 'No company'}</p>
                
                <div class="space-y-2">
                    ${lead.email ? `
                        <div class="text-sm text-gray-600 truncate">${lead.email}</div>
                    ` : ''}
                    ${lead.phone ? `
                        <div class="text-sm text-gray-600">${lead.phone}</div>
                    ` : ''}
                </div>
                
                ${lead.lead_source ? `
                    <div class="mt-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                            ${lead.lead_source}
                        </span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // ... continuing with utility methods and more functionality
}

// Initialize the enhanced lead manager
window.EnhancedLeadManager = EnhancedLeadManager;

    /**
     * Utility methods for enhanced lead manager
     */
    getStatusColor(lead) {
        if (lead.disqualified) return 'status-unqualified';
        if (lead.was_in_touch) return 'status-contacted';
        if (lead.qualified) return 'status-qualified';
        return 'status-new';
    }

    getStatusText(lead) {
        if (lead.disqualified) return 'Disqualified';
        if (lead.was_in_touch) return 'Contacted';
        if (lead.qualified) return 'Qualified';
        return 'New';
    }

    getGradientColors(lead) {
        const colors = ['gradient-blue', 'gradient-green', 'gradient-purple', 'gradient-orange', 'gradient-pink', 'gradient-teal'];
        const index = (lead.id || 0) % colors.length;
        return colors[index];
    }

    getPriorityIcon(priority) {
        switch (priority) {
            case 'high': return '<span class="priority-high">🔥</span>';
            case 'medium': return '<span class="priority-medium">⚡</span>';
            case 'low': return '<span class="priority-low">📌</span>';
            default: return '';
        }
    }

    getSortIcon(field) {
        if (this.sortConfig.field !== field) {
            return '<svg class="sort-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/></svg>';
        }
        
        const direction = this.sortConfig.direction;
        return direction === 'asc' 
            ? '<svg class="sort-icon active" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/></svg>'
            : '<svg class="sort-icon active" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/></svg>';
    }

    formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString();
    }

    formatRelativeTime(dateString) {
        if (!dateString) return '';
        
        const now = new Date();
        const date = new Date(dateString);
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return this.formatDate(dateString);
    }

    groupLeadsByStatus(leads) {
        const groups = {
            new: [],
            contacted: [],
            qualified: [],
            unqualified: []
        };
        
        leads.forEach(lead => {
            if (lead.disqualified) {
                groups.unqualified.push(lead);
            } else if (lead.qualified) {
                groups.qualified.push(lead);
            } else if (lead.was_in_touch) {
                groups.contacted.push(lead);
            } else {
                groups.new.push(lead);
            }
        });
        
        return groups;
    }

    /**
     * Enhanced interaction methods
     */
    async performSearch(term) {
        this.searchTerm = term;
        this.currentPage = 1;
        
        // Show search spinner
        const spinner = document.getElementById('search-spinner');
        if (spinner) {
            spinner.classList.remove('hidden');
        }
        
        try {
            await this.loadLeadsList();
        } finally {
            if (spinner) {
                spinner.classList.add('hidden');
            }
        }
    }

    applyQuickFilter(type, value) {
        if (value) {
            this.filters.set(type, value);
        } else {
            this.filters.delete(type);
        }
        
        this.currentPage = 1;
        this.loadLeadsList();
    }

    switchView(view) {
        this.currentView = view;
        this.loadLeadsList();
        
        // Update view switcher
        const switcher = document.getElementById('view-switcher');
        if (switcher) {
            switcher.querySelector('select').value = view;
        }
    }

    toggleFilters() {
        const filters = document.getElementById('advanced-filters');
        if (filters) {
            filters.classList.toggle('hidden');
            filters.classList.toggle('show');
        }
    }

    sortBy(field) {
        if (this.sortConfig.field === field) {
            this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortConfig.field = field;
            this.sortConfig.direction = 'asc';
        }
        
        this.loadLeadsList();
    }

    toggleLeadSelection(leadId) {
        if (this.selectedLeads.has(leadId)) {
            this.selectedLeads.delete(leadId);
        } else {
            this.selectedLeads.add(leadId);
        }
        
        this.updateBulkActionsBar();
    }

    selectAll() {
        const checkboxes = document.querySelectorAll('.lead-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            this.selectedLeads.add(parseInt(checkbox.value));
        });
        
        this.updateBulkActionsBar();
    }

    clearSelection() {
        this.selectedLeads.clear();
        document.querySelectorAll('.lead-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        this.updateBulkActionsBar();
    }

    updateBulkActionsBar() {
        const bar = document.getElementById('bulk-actions-bar');
        const count = document.getElementById('selected-count');
        
        if (this.selectedLeads.size > 0) {
            bar.classList.remove('hidden');
            count.textContent = this.selectedLeads.size;
        } else {
            bar.classList.add('hidden');
        }
    }

    updateCounts(total) {
        const countElement = document.getElementById('leads-count');
        if (countElement) {
            countElement.textContent = `${total} lead${total !== 1 ? 's' : ''}`;
        }
        
        const totalElement = document.getElementById('total-count');
        if (totalElement) {
            totalElement.textContent = total;
        }
    }

    updatePagination(total) {
        const totalPages = Math.ceil(total / this.pageSize);
        const pagination = document.getElementById('leads-pagination');
        
        if (totalPages <= 1) {
            pagination.classList.add('hidden');
            return;
        }
        
        pagination.classList.remove('hidden');
        
        // Update pagination info
        const showingFrom = ((this.currentPage - 1) * this.pageSize) + 1;
        const showingTo = Math.min(this.currentPage * this.pageSize, total);
        
        document.getElementById('showing-from').textContent = showingFrom;
        document.getElementById('showing-to').textContent = showingTo;
        document.getElementById('showing-total').textContent = total;
        
        // Update buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= totalPages;
        
        // Generate page numbers
        this.generatePageNumbers(totalPages);
    }

    generatePageNumbers(totalPages) {
        const container = document.getElementById('page-numbers');
        container.innerHTML = '';
        
        const maxVisible = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);
        
        if (endPage - startPage + 1 < maxVisible) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const button = document.createElement('button');
            button.textContent = i;
            button.className = i === this.currentPage 
                ? 'px-3 py-1 bg-blue-600 text-white rounded text-sm'
                : 'px-3 py-1 text-gray-700 hover:bg-gray-100 rounded text-sm';
            
            button.onclick = () => {
                this.currentPage = i;
                this.loadLeadsList();
            };
            
            container.appendChild(button);
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadLeadsList();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.totalCount / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.loadLeadsList();
        }
    }

    changePageSize(size) {
        this.pageSize = parseInt(size);
        this.currentPage = 1;
        this.loadLeadsList();
    }

    /**
     * Enhanced form with UX improvements
     */
    async showLeadForm(leadId = null) {
        try {
            let lead = null;
            
            if (leadId) {
                lead = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/`);
            }
            
            // Create enhanced modal with UX improvements
            const modal = document.createElement('div');
            modal.className = 'modal-overlay fade-in';
            
            modal.innerHTML = `
                <div class="modal scale-in max-w-5xl w-full mx-4">
                    <div class="modal-header">
                        <h2 class="modal-title">${leadId ? 'Edit Lead' : 'Create New Lead'}</h2>
                        <button onclick="this.closest('.modal-overlay').remove(); document.body.style.overflow = '';" 
                                class="text-gray-400 hover:text-gray-600 focus:outline-none">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="modal-body">
                        <form id="enhanced-lead-form" class="space-y-8">
                            ${this.renderEnhancedForm(lead)}
                        </form>
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" 
                                onclick="this.closest('.modal-overlay').remove(); document.body.style.overflow = '';"
                                class="btn-secondary">
                            Cancel
                        </button>
                        <button type="button" 
                                onclick="app.leads.saveEnhancedLead(${leadId || 'null'})"
                                class="btn-primary">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                            </svg>
                            ${leadId ? 'Update Lead' : 'Create Lead'}
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';
            
            // Initialize UX enhancements for the form
            const form = modal.querySelector('#enhanced-lead-form');
            window.uxEnhancements.applySmartDefaults(form, lead || {});
            window.uxEnhancements.setupAdvancedValidation(form);
            
            // Focus first input
            setTimeout(() => {
                const firstInput = form.querySelector('input');
                if (firstInput) firstInput.focus();
            }, 100);
            
        } catch (error) {
            console.error('Error loading enhanced lead form:', error);
            this.app.showToast('Failed to load lead form', 'error');
        }
    }

    renderEnhancedForm(lead) {
        return `
            <!-- Progress Indicator -->
            <div class="mb-6">
                <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-500">Step 1 of 4</span>
                    <span class="text-gray-500" id="form-progress">0% complete</span>
                </div>
                <div class="progress-bar mt-2">
                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                </div>
            </div>
            
            <!-- Form Sections -->
            <div class="space-y-8">
                <!-- Essential Information -->
                <div class="form-section" id="section-essential">
                    <div class="flex items-center mb-6">
                        <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">
                            1
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900">Essential Information</h3>
                        <span class="ml-2 text-sm text-red-500">*Required</span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="form-group">
                            <label class="form-label required" for="first_name">First Name</label>
                            <input type="text" 
                                   id="first_name" 
                                   name="first_name" 
                                   class="form-input"
                                   value="${lead?.first_name || ''}"
                                   placeholder="Enter first name"
                                   required>
                            <div class="form-hint">Or company name if this is a business lead</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="last_name">Last Name</label>
                            <input type="text" 
                                   id="last_name" 
                                   name="last_name" 
                                   class="form-input"
                                   value="${lead?.last_name || ''}"
                                   placeholder="Enter last name">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label required" for="email">Email Address</label>
                            <input type="email" 
                                   id="email" 
                                   name="email" 
                                   class="form-input"
                                   value="${lead?.email || ''}"
                                   placeholder="Enter email address"
                                   required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="phone">Phone Number</label>
                            <input type="tel" 
                                   id="phone" 
                                   name="phone" 
                                   class="form-input"
                                   value="${lead?.phone || ''}"
                                   placeholder="Enter phone number">
                        </div>
                        
                        <div class="form-group md:col-span-2">
                            <label class="form-label" for="company_name">Company Name</label>
                            <input type="text" 
                                   id="company_name" 
                                   name="company_name" 
                                   class="form-input"
                                   value="${lead?.company_name || ''}"
                                   placeholder="Enter company name">
                            <div class="form-hint">We'll auto-suggest based on email domain</div>
                        </div>
                    </div>
                </div>
                
                <!-- Additional Details -->
                <div class="form-section hidden" id="section-details">
                    <div class="flex items-center mb-6">
                        <div class="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center mr-3">
                            2
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900">Additional Details</h3>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="form-group">
                            <label class="form-label" for="title">Job Title</label>
                            <input type="text" 
                                   id="title" 
                                   name="title" 
                                   class="form-input"
                                   value="${lead?.title || ''}"
                                   placeholder="e.g. CEO, Manager, Developer">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="website">Website</label>
                            <input type="url" 
                                   id="website" 
                                   name="website" 
                                   class="form-input"
                                   value="${lead?.website || ''}"
                                   placeholder="https://example.com">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="secondary_email">Secondary Email</label>
                            <input type="email" 
                                   id="secondary_email" 
                                   name="secondary_email" 
                                   class="form-input"
                                   value="${lead?.secondary_email || ''}"
                                   placeholder="Alternative email address">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="mobile">Mobile Phone</label>
                            <input type="tel" 
                                   id="mobile" 
                                   name="mobile" 
                                   class="form-input"
                                   value="${lead?.mobile || ''}"
                                   placeholder="Mobile number">
                        </div>
                    </div>
                </div>
                
                <!-- Location & Company -->
                <div class="form-section hidden" id="section-location">
                    <div class="flex items-center mb-6">
                        <div class="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center mr-3">
                            3
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900">Location & Company</h3>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="form-group md:col-span-2">
                            <label class="form-label" for="address">Address</label>
                            <input type="text" 
                                   id="address" 
                                   name="address" 
                                   class="form-input"
                                   value="${lead?.address || ''}"
                                   placeholder="Street address">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="city_name">City</label>
                            <input type="text" 
                                   id="city_name" 
                                   name="city_name" 
                                   class="form-input"
                                   value="${lead?.city_name || ''}"
                                   placeholder="City">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="region">Region/State</label>
                            <input type="text" 
                                   id="region" 
                                   name="region" 
                                   class="form-input"
                                   value="${lead?.region || ''}"
                                   placeholder="State or region">
                        </div>
                        
                        <div class="form-group md:col-span-2">
                            <label class="form-label" for="company_address">Company Address</label>
                            <input type="text" 
                                   id="company_address" 
                                   name="company_address" 
                                   class="form-input"
                                   value="${lead?.company_address || ''}"
                                   placeholder="Company address (if different)">
                        </div>
                    </div>
                </div>
                
                <!-- Final Details -->
                <div class="form-section hidden" id="section-final">
                    <div class="flex items-center mb-6">
                        <div class="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center mr-3">
                            4
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900">Final Details</h3>
                    </div>
                    
                    <div class="space-y-6">
                        <div class="form-group">
                            <label class="form-label" for="description">Notes & Description</label>
                            <textarea id="description" 
                                      name="description" 
                                      rows="4"
                                      class="form-input"
                                      placeholder="Add any notes or additional information about this lead...">${lead?.description || ''}</textarea>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-4">
                                <div class="flex items-center">
                                    <input type="checkbox" 
                                           id="was_in_touch" 
                                           name="was_in_touch" 
                                           class="rounded"
                                           ${lead?.was_in_touch ? 'checked' : ''}>
                                    <label for="was_in_touch" class="ml-2 text-sm text-gray-700">
                                        Already been in touch with this lead
                                    </label>
                                </div>
                                
                                <div class="flex items-center">
                                    <input type="checkbox" 
                                           id="disqualified" 
                                           name="disqualified" 
                                           class="rounded"
                                           ${lead?.disqualified ? 'checked' : ''}>
                                    <label for="disqualified" class="ml-2 text-sm text-gray-700">
                                        Mark as disqualified
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show empty state when no leads found
     */
    showEmptyState(container) {
        const hasFilters = this.searchTerm || this.filters.size > 0;
        
        container.innerHTML = `
            <div class="text-center py-12">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900">
                    ${hasFilters ? 'No leads found' : 'No leads yet'}
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                    ${hasFilters 
                        ? 'Try adjusting your search or filters to find what you\'re looking for.' 
                        : 'Get started by creating your first lead.'}
                </p>
                <div class="mt-6">
                    ${hasFilters ? `
                        <button onclick="app.leads.clearAllFilters()" class="btn-secondary mr-3">
                            Clear Filters
                        </button>
                    ` : ''}
                    <button onclick="app.leads.showLeadForm()" class="btn-primary">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                        </svg>
                        Create Lead
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Show error state
     */
    showErrorState(container, error) {
        container.innerHTML = `
            <div class="text-center py-12">
                <svg class="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900">
                    Unable to load leads
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                    There was an error loading the leads. Please try again.
                </p>
                <div class="mt-6">
                    <button onclick="app.leads.loadLeadsList()" class="btn-primary">
                        Try Again
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Additional methods for enhanced functionality
     */
    async loadFilterOptions() {
        // Load data for filter dropdowns
        try {
            const [sources, owners] = await Promise.all([
                window.apiClient.get('lead-sources/').catch(() => ({results: []})),
                window.apiClient.get('users/').catch(() => ({results: []}))
            ]);
            
            // Populate source filter
            const sourceFilter = document.getElementById('source-filter');
            if (sourceFilter && sources.results) {
                sources.results.forEach(source => {
                    const option = document.createElement('option');
                    option.value = source.id;
                    option.textContent = source.name;
                    sourceFilter.appendChild(option);
                });
            }
            
            // Populate owner filter
            const ownerFilter = document.getElementById('owner-filter');
            if (ownerFilter && owners.results) {
                owners.results.forEach(owner => {
                    const option = document.createElement('option');
                    option.value = owner.id;
                    option.textContent = owner.full_name || `${owner.first_name} ${owner.last_name}`;
                    ownerFilter.appendChild(option);
                });
            }
            
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }
}

// Replace the original LeadManager with EnhancedLeadManager
if (typeof window !== 'undefined') {
    window.EnhancedLeadManager = EnhancedLeadManager;
}
