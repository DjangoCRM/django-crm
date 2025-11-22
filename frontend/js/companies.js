// Company management functionality
class CompanyManager {
    constructor(app) {
        this.app = app;
    }

    async loadCompanies() {
        const section = document.getElementById('companies-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Companies</h2>
                        <div class="flex space-x-2">
                            <input type="text" id="company-search" placeholder="Search companies..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                            <button onclick="app.companies.showCompanyForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
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
            const companies = await this.app.apiCall(`/v1/companies/?${searchParam}`);
            const content = document.getElementById('companies-content');
            
            if (!companies.results || companies.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            🏢
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm ? 'No companies found for your search' : 'No companies found'}</p>
                        <button onclick="app.companies.showCompanyForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
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
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${companies.results.map(company => `
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold">
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
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${company.disqualified ? 'bg-red-100 text-red-800' : company.active ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                                            ${company.disqualified ? 'Disqualified' : company.active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button onclick="app.companies.viewCompany(${company.id})" class="text-primary-600 hover:text-primary-900">View</button>
                                            <button onclick="app.companies.editCompany(${company.id})" class="text-yellow-600 hover:text-yellow-900">Edit</button>
                                            <button onclick="app.companies.deleteCompany(${company.id})" class="text-red-600 hover:text-red-900">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (error) {
            document.getElementById('companies-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading companies</div>';
        }
    }

    searchCompanies(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadCompaniesList(term);
        }, 300);
    }

    showCompanyForm(companyId = null) {
        const isEdit = companyId !== null;
        const title = isEdit ? 'Edit Company' : 'Add New Company';

        const modal = document.createElement('div');
        modal.id = 'company-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('company-modal').remove()" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="company-form" class="p-6 space-y-4">
                    <div>
                        <label for="full_name" class="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
                        <input type="text" id="full_name" name="full_name" required
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="website" class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                            <input type="url" id="website" name="website"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        <div>
                            <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                            <input type="tel" id="phone" name="phone"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                    </div>
                    
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" id="email" name="email"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="city_name" class="block text-sm font-medium text-gray-700 mb-1">City</label>
                            <input type="text" id="city_name" name="city_name"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        <div>
                            <label for="country" class="block text-sm font-medium text-gray-700 mb-1">Country</label>
                            <select id="country" name="country" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Country</option>
                            </select>
                        </div>
                    </div>
                    
                    <div>
                        <label for="address" class="block text-sm font-medium text-gray-700 mb-1">Address</label>
                        <textarea id="address" name="address" rows="2"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea id="description" name="description" rows="3"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                    </div>
                    
                    <div class="flex items-center space-x-6">
                        <div class="flex items-center">
                            <input type="checkbox" id="active" name="active" checked
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="active" class="ml-2 block text-sm text-gray-900">Active</label>
                        </div>
                        <div class="flex items-center">
                            <input type="checkbox" id="disqualified" name="disqualified"
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="disqualified" class="ml-2 block text-sm text-gray-900">Disqualified</label>
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="document.getElementById('company-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                            ${isEdit ? 'Update' : 'Create'} Company
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        if (isEdit) {
            this.loadCompanyData(companyId);
        }

        document.getElementById('company-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCompany(companyId);
        });
    }

    async loadCompanyData(companyId) {
        try {
            const company = await this.app.apiCall(`/v1/companies/${companyId}/`);
            
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
            const url = companyId ? `/v1/companies/${companyId}/` : '/v1/companies/';
            
            await this.app.apiCall(url, {
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
            await this.app.apiCall(`/v1/companies/${companyId}/`, { method: 'DELETE' });
            this.loadCompaniesList();
            this.app.showToast('Company deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting company', 'error');
        }
    }

    async viewCompany(companyId) {
        try {
            const company = await this.app.apiCall(`/v1/companies/${companyId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'company-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Company Details</h3>
                            <button onclick="document.getElementById('company-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                <div class="h-20 w-20 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white text-2xl font-bold">
                                    ${company.full_name.charAt(0).toUpperCase()}
                                </div>
                            </div>
                            
                            <div class="flex-1">
                                <h4 class="text-xl font-bold text-gray-900">${company.full_name}</h4>
                                ${company.website ? `<a href="${company.website}" target="_blank" class="text-primary-600 hover:text-primary-800">${company.website}</a>` : ''}
                                
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
                                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${company.disqualified ? 'bg-red-100 text-red-800' : company.active ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
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
                                    <button onclick="app.companies.editCompany(${company.id}); document.getElementById('company-view-modal').remove();" 
                                            class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
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