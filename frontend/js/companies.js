// Company management functionality
class CompanyManager {
    constructor(app) {
        this.app = app;
    }

    async loadCompanies() {
        const section = document.getElementById('companies-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow dark:bg-slate-800">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Companies</h2>
                        <div class="flex space-x-2">
                            <input type="text" id="company-search" placeholder="Search companies..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                            <button data-action="companies.showCompanyForm" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                                Add Company
                            </button>
                        </div>
                    </div>
                </div>
                <div id="companies-content" class="p-6">
                    <div class="htmx-indicator">Loading companies...</div>
                </div>
            </div>
        `;

        document.getElementById('company-search').addEventListener('input', (e) => {
            this.searchCompanies(e.target.value);
        });
        
        if (this.app.token) {
            this.loadCompaniesList();
        }
    }

    async loadCompaniesList(searchTerm = '') {
        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const companies = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.COMPANIES}?${searchParam}`);
            const content = document.getElementById('companies-content');
            
            if (!companies.results || companies.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            🏢
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm ? 'No companies found for your search' : 'No companies found'}</p>
                        <button data-action="companies.showCompanyForm" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                            Add Your First Company
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Industry</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact Info</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class=\"bg-white divide-y divide-gray-200 dark:bg-slate-800 dark:divide-slate-700\">
                            ${companies.results.map(company => `
                                <tr class="hover:bg-gray-50 dark:hover:bg-slate-700">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-lg bg-primary flex items-center justify-center text-white font-medium">
                                                    ${company.full_name.charAt(0).toUpperCase()}
                                                </div>
                                            </div>
                                            <div class="ml-4">
                                                <div class="text-sm font-medium text-gray-900">${company.full_name}</div>
                                                <div class="text-sm text-gray-500">${company.website || 'No website'}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${company.industry_names || 'No industry'}</div>
                                        <div class="text-sm text-gray-500">${company.type_name || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${company.city_name || 'No city'}</div>
                                        <div class="text-sm text-gray-500">${company.country_name || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${company.email || 'No email'}</div>
                                        <div class="text-sm text-gray-500">${company.phone || 'No phone'}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${company.disqualified ? 'bg-danger bg-opacity-20 text-danger' : company.active ? 'bg-success bg-opacity-20 text-success' : 'bg-warning bg-opacity-20 text-warning'}">
                                            ${company.disqualified ? 'Disqualified' : company.active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button data-action="companies.viewCompany" data-id="${company.id}" class="text-primary hover:text-primary-900">View</button>
                                            <button data-action="companies.editCompany" data-id="${company.id}" class="text-warning hover:text-yellow-900">Edit</button>
                                            <button data-action="companies.deleteCompany" data-id="${company.id}" class="text-danger hover:text-red-900">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (error) {
            document.getElementById('companies-content').innerHTML = '<div class="text-danger text-center py-4">Error loading companies</div>';
        }
    }

    searchCompanies(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadCompaniesList(term);
        }, 300);
    }



    async loadCompanyData(companyId) {
        try {
            const company = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.COMPANIES}${companyId}/`);
            
            const fields = ['full_name', 'website', 'phone', 'email', 'city_name', 'address', 'description'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && company[field]) {
                    element.value = company[field];
                }
            });

            document.getElementById('active').checked = company.active;
            document.getElementById('disqualified').checked = company.disqualified;

            if (company.country) {
                document.getElementById('country').value = company.country;
            }

        } catch (error) {
            this.app.showToast('Error loading company data', 'error');
        }
    }

    async saveCompany(companyId = null) {
        const formData = new FormData(document.getElementById('company-form'));
        const companyData = Object.fromEntries(formData.entries());
        
        companyData.active = document.getElementById('active').checked;
        companyData.disqualified = document.getElementById('disqualified').checked;
        
        if (!companyData.country) {
            delete companyData.country;
        }

        try {
            const method = companyId ? 'PUT' : 'POST';
            const url = companyId ? `${window.CRM_CONFIG.ENDPOINTS.COMPANIES}${companyId}/` : window.CRM_CONFIG.ENDPOINTS.COMPANIES;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(companyData)
            });

            document.getElementById('company-modal').remove();
            this.loadCompaniesList();
            this.app.showToast(`Company ${companyId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${companyId ? 'updating' : 'creating'} company`, 'error');
        }
    }

    async editCompany(companyId) {
        this.showCompanyForm(companyId);
    }

    async deleteCompany(companyId) {
        if (!confirm('Are you sure you want to delete this company?')) {
            return;
        }

        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.COMPANIES}${companyId}/`);
            this.loadCompaniesList();
            this.app.showToast('Company deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting company', 'error');
        }
    }

    async viewCompany(companyId) {
        try {
            const company = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.COMPANIES}${companyId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'company-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Company Details</h3>
                            <button data-action="companies.closeViewCompanyModal" class="text-gray-400 hover:text-gray-600">
                                <span class="sr-only">Close</span>
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div class="p-6">
                        <div class="flex items-start space-x-6">
                            <div class="flex-shrink-0">
                                <div class="h-20 w-20 rounded-lg bg-primary flex items-center justify-center text-white text-2xl font-bold">
                                    ${company.full_name.charAt(0).toUpperCase()}
                                </div>
                            </div>
                            
                            <div class="flex-1">
                                <h4 class="text-xl font-bold text-gray-900">${company.full_name}</h4>
                                ${company.website ? `<a href="${company.website}" target="_blank" class="text-primary hover:text-primary-800">${company.website}</a>` : ''}
                                
                                <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <dl class="space-y-3">
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Email</dt>
                                                <dd class="text-sm text-gray-900">${company.email || 'No email'}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Phone</dt>
                                                <dd class="text-sm text-gray-900">${company.phone || 'No phone'}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Location</dt>
                                                <dd class="text-sm text-gray-900">${[company.city_name, company.country_name].filter(Boolean).join(', ') || 'No location'}</dd>
                                            </div>
                                        </dl>
                                    </div>
                                    
                                    <div>
                                        <dl class="space-y-3">
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Status</dt>
                                                <dd class="text-sm">
                                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${company.disqualified ? 'bg-danger bg-opacity-20 text-danger' : company.active ? 'bg-success bg-opacity-20 text-success' : 'bg-warning bg-opacity-20 text-warning'}">
                                                        ${company.disqualified ? 'Disqualified' : company.active ? 'Active' : 'Inactive'}
                                                    </span>
                                                </dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Created</dt>
                                                <dd class="text-sm text-gray-900">${new Date(company.creation_date).toLocaleDateString()}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                                <dd class="text-sm text-gray-900">${new Date(company.update_date).toLocaleDateString()}</dd>
                                            </div>
                                        </dl>
                                    </div>
                                </div>
                                
                                ${company.address ? `
                                    <div class="mt-4">
                                        <dt class="text-sm font-medium text-gray-500">Address</dt>
                                        <dd class="mt-1 text-sm text-gray-900">${company.address}</dd>
                                    </div>
                                ` : ''}
                                
                                ${company.description ? `
                                    <div class="mt-4">
                                        <dt class="text-sm font-medium text-gray-500">Description</dt>
                                        <dd class="mt-1 text-sm text-gray-900">${company.description}</dd>
                                    </div>
                                ` : ''}
                                
                                <div class="mt-6 flex justify-end space-x-3">
                                    <button data-action="companies.editCompany" data-id="${company.id}" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90">
                                        Edit Company
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading company details', 'error');
        }
    }
}
/* ===== Merged UX patches from companies-ux.js ===== */

/**
 * UX Enhancements for Companies Module
 */

if (typeof CompanyManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadCompaniesList with skeleton and empty states
    const originalLoadCompaniesList = CompanyManager.prototype.loadCompaniesList;
    CompanyManager.prototype.loadCompaniesList = async function(searchTerm = '') {
        const content = document.getElementById('companies-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'cards', 6);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const companies = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.COMPANIES}?${searchParam}`);
            
            if (!companies.results || companies.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '🏢',
                    title: searchTerm ? 'No companies found' : 'No companies yet',
                    description: searchTerm 
                        ? `No companies match "${searchTerm}"`
                        : 'Start by adding your first company',
                    actionLabel: 'Add Company',
                    actionHandler: 'app.companies.showCompanyForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("company-search").value=""; app.companies.loadCompaniesList()'
                    } : null
                });
                return;
            }

            // Render with mobile support
            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${companies.results.map(company => this.renderCompanyCard(company)).join('')}
                </div>
                
                ${companies.count > companies.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-surface-600">
                            Showing ${companies.results.length} of ${companies.count} companies
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-secondary btn-sm">Previous</button>
                            <button class="btn btn-secondary btn-sm">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;
        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load companies',
                message: 'Unable to fetch companies from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.companies.loadCompaniesList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Render company card with better styling
    CompanyManager.prototype.renderCompanyCard = function(company) {
        return `
            <div class="card p-6 hover:shadow-medium transition-shadow" data-id="${company.id}">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <div class="avatar avatar-lg bg-primary-100">
                            <span class="text-primary-600 text-xl font-bold">
                                ${(company.full_name || '?').charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-surface-900">${company.full_name}</h3>
                            ${company.website ? `<a href="${company.website}" target="_blank" class="text-sm text-primary-600 hover:underline">${company.website}</a>` : ''}
                        </div>
                    </div>
                </div>
                
                <div class="space-y-2 mb-4">
                    ${company.email ? `
                        <div class="flex items-center gap-2 text-sm text-surface-700">
                            <svg class="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                            </svg>
                            ${company.email}
                        </div>
                    ` : ''}
                    ${company.phone ? `
                        <div class="flex items-center gap-2 text-sm text-surface-700">
                            <svg class="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                            </svg>
                            ${company.phone}
                        </div>
                    ` : ''}
                    ${company.city_name ? `
                        <div class="flex items-center gap-2 text-sm text-surface-700">
                            <svg class="w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            ${company.city_name}
                        </div>
                    ` : ''}
                </div>
                
                <div class="flex gap-2 pt-4 border-t border-surface-200">
                    <button data-action="companies.viewCompany" data-id="${company.id}" class="btn btn-secondary btn-sm flex-1">
                        View
                    </button>
                    <button data-action="companies.editCompany" data-id="${company.id}" class="btn btn-text btn-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                    <button data-action="companies.deleteCompany" data-id="${company.id}" class="btn btn-text btn-sm text-error-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    };

    // Enhanced showCompanyForm with smart defaults
    const originalShowCompanyForm = CompanyManager.prototype.showCompanyForm;
    CompanyManager.prototype.showCompanyForm = function(companyId = null) {
        const isEdit = companyId !== null;
        const title = isEdit ? 'Edit Company' : 'Add New Company';

        const modal = document.createElement('div');
        modal.id = 'company-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('company-modal').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="company-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <label for="full_name" class="input-label">Company Name *</label>
                        <input type="text" id="full_name" name="full_name" required class="input" placeholder="Acme Corporation">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="email" class="input-label">Email</label>
                            <input type="email" id="email" name="email" class="input" placeholder="info@company.com">
                            <p class="input-hint">Will be converted to lowercase</p>
                        </div>
                        <div class="input-group">
                            <label for="phone" class="input-label">Phone</label>
                            <input type="tel" id="phone" name="phone" class="input" placeholder="+1234567890">
                            <p class="input-hint">Will be cleaned to +digits format</p>
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="website" class="input-label">Website</label>
                        <input type="url" id="website" name="website" class="input" placeholder="https://company.com">
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <!-- Advanced fields -->
                    <div class="input-group" data-advanced="true">
                        <label for="industry" class="input-label">Industry</label>
                        <input type="text" id="industry" name="industry" class="input">
                    </div>
                    
                    <div class="input-group" data-advanced="true">
                        <label for="employees" class="input-label">Number of Employees</label>
                        <input type="number" id="employees" name="employees" class="input">
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('company-modal').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="company-form" class="btn btn-primary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${isEdit ? 'Update' : 'Create'} Company
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Disable background scroll and setup close handlers
        document.body.style.overflow = 'hidden';
        const overlayEl = modal; // .modal-overlay
        const dialogEl = modal.querySelector('.modal');
        const closeModal = () => {
            overlayEl.remove();
            document.body.style.overflow = '';
            document.removeEventListener('keydown', onKeyDown);
        };
        const onKeyDown = (e) => { if (e.key === 'Escape') closeModal(); };
        document.addEventListener('keydown', onKeyDown);
        overlayEl.addEventListener('click', (e) => { if (!dialogEl.contains(e.target)) closeModal(); });
        // a11y focus trap
        window.uxEnhancements?.applyFocusTrap(overlayEl);
        dialogEl.setAttribute('aria-label', title);
        
        const companyForm = document.getElementById('company-form');

        // Progressive disclosure
        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(companyForm);
        }

        // Smart defaults for new companies
        if (!isEdit && window.uxEnhancements) {
            const defaults = window.uxEnhancements.getSmartDefaults('company', this.app.user?.id);
            window.uxEnhancements.applySmartDefaults(companyForm, defaults);
        }

        if (isEdit) {
            this.loadCompanyData(companyId);
        }

        // Setup form submission
        companyForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCompany(companyId);
        });

        // Setup normalization and validation
        if (window.FormValidators) {
            window.FormValidators.setupFormNormalization(companyForm);
            window.FormValidators.setupFormValidation(companyForm);
        }

        // Focus first input
        setTimeout(() => document.getElementById('full_name').focus(), 100);
    };

    // Enhanced saveCompany with optimistic updates
    const originalSaveCompany = CompanyManager.prototype.saveCompany;
    CompanyManager.prototype.saveCompany = async function(companyId = null) {
        const formData = new FormData(document.getElementById('company-form'));
        const companyData = Object.fromEntries(formData.entries());
        
        // Remember values
        if (window.uxEnhancements && companyData.industry) {
            window.uxEnhancements.rememberValue('industry', companyData.industry);
        }

        try {
            const method = companyId ? 'PUT' : 'POST';
            const url = companyId 
                ? `${window.CRM_CONFIG.ENDPOINTS.COMPANIES}${companyId}/` 
                : window.CRM_CONFIG.ENDPOINTS.COMPANIES;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(companyData)
            });

            document.getElementById('company-modal').remove();
            this.loadCompaniesList();
            this.app.showToast(
                `Company ${companyId ? 'updated' : 'created'} successfully`, 
                'success'
            );
        } catch (error) {
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: `Failed to ${companyId ? 'update' : 'create'} company`,
                    message: error.message || 'Please check your input and try again.',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: `app.companies.saveCompany(${companyId})`, primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            } else {
                this.app.showToast(`Error ${companyId ? 'updating' : 'creating'} company`, 'error');
            }
        }
    };

    // Setup search progress
    const originalLoadCompanies = CompanyManager.prototype.loadCompanies;
    CompanyManager.prototype.loadCompanies = function() {
        originalLoadCompanies.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('company-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadCompaniesList(term);
                });
            }
        }, 100);
    };
}
