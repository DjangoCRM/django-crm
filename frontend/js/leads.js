// Lead management functionality
class LeadManager {
    // Helpers for prompts
    async prompt(text, def='') {
        const v = window.prompt(text, def);
        if (v === null) throw new Error('cancelled');
        return v.trim();
    }
    constructor(app) {
        this.app = app;
    }

    async loadLeads() {
        this.selected = new Set();
        const section = document.getElementById('leads-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Leads</h2>
                        <div class="flex space-x-2">
                            <select id="lead-status-filter" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                                <option value="">All Leads</option>
                                <option value="false">Active</option>
                                <option value="true">Disqualified</option>
                            </select>
                            <input type="text" id="lead-search" placeholder="Search leads..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                            <button onclick="app.leads.showLeadForm()" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                                Add Lead
                            </button>
                        </div>
                    </div>
                </div>
                <div class="px-6 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                   <div class="flex items-center space-x-3">
                       <label class="inline-flex items-center space-x-2">
                           <input id="leads-select-all" type="checkbox" class="rounded" />
                           <span class="text-sm text-gray-600">Select all</span>
                       </label>
                       <div class="flex items-center space-x-2">
                           <button onclick="app.leads.openBulkAssignDialog()" class="px-3 py-1.5 bg-primary text-white rounded text-sm hover:bg-opacity-90">Bulk Assign</button>
                           <button onclick="app.leads.openBulkTagDialog()" class="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm hover:bg-opacity-90">Bulk Tag</button>
                           <button onclick="app.leads.openBulkDisqualifyDialog()" class="px-3 py-1.5 bg-danger text-white rounded text-sm hover:bg-opacity-90">Bulk Disqualify</button>
                       </div>
                   </div>
                   <div class="text-sm text-gray-500">Selected: <span id="leads-selected-count">0</span></div>
                </div>
                <div id="leads-content" class="p-6">
                    <div class="htmx-indicator">Loading leads...</div>
                </div>
            </div>
        `;

        document.getElementById('lead-search').addEventListener('input', (e) => {
            this.searchLeads(e.target.value);
        });

        document.getElementById('lead-status-filter').addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });
        
        // Select all handler
        document.getElementById('leads-select-all').addEventListener('change', (e) => {
            const check = e.target.checked;
            const boxes = document.querySelectorAll('#leads-content input[type="checkbox"]');
            boxes.forEach(b => { b.checked = check; const id = Number((b.getAttribute('onchange')||'').match(/toggleSelected\((\d+)/)?.[1]); if (id) this.toggleSelected(id, check); });
        });
        
        if (this.app.token) {
            this.loadLeadsList();
        }
    }

    async loadLeadsList(searchTerm = '', statusFilter = '') {
        try {
            let url = '/v1/leads/?';
            if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
            if (statusFilter) url += `disqualified=${statusFilter}&`;
            
            const leads = await this.app.apiCall(url);
            const content = document.getElementById('leads-content');
            
            if (!leads.results || leads.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            🎯
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm || statusFilter ? 'No leads found for your criteria' : 'No leads found'}</p>
                        <button onclick="app.leads.showLeadForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                            Add Your First Lead
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${leads.results.map(lead => `
                        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                             onclick="app.leads.viewLead(${lead.id})">
                            <div class="flex items-start justify-between mb-3">
                                <div class="flex items-center space-x-3">
                                    <div class="flex-shrink-0 h-10 w-10">
                                        <div class="h-10 w-10 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white font-medium">
                                            ${this.getInitials(lead.first_name, lead.last_name)}
                                        </div>
                                    </div>
                                    <div>
                                        <h3 class="text-lg font-medium text-gray-900">${lead.full_name}</h3>
                                        <p class="text-sm text-gray-500">${lead.company_name || 'No company'}</p>
                                    </div>
                                </div>
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${lead.disqualified ? 'bg-danger bg-opacity-20 text-danger' : 'bg-success bg-opacity-20 text-success'}">
                                    ${lead.disqualified ? 'Disqualified' : 'Active'}
                                </span>
                            </div>
                            
                            <div class="space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Email:</span>
                                    <span class="text-sm text-gray-900 truncate">${lead.email || 'No email'}</span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Phone:</span>
                                    <span class="text-sm text-gray-900">${lead.phone || 'No phone'}</span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Source:</span>
                                    <span class="text-sm text-gray-900">${lead.lead_source_name || 'Unknown'}</span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Location:</span>
                                    <span class="text-sm text-gray-900">${lead.city_name || lead.country_name || 'No location'}</span>
                                </div>
                            </div>
                            
                            <div class="mt-4 flex justify-between items-center">
                                <div class="flex items-center space-x-2">
                                    ${lead.was_in_touch ? '<span class="text-green-500 text-xs">✓ Contacted</span>' : '<span class="text-gray-400 text-xs">Not contacted</span>'}
                                </div>
                                
                                <div class="flex space-x-1">
                                    <button onclick="event.stopPropagation(); app.leads.convertLead(${lead.id})" 
                                            class="text-green-600 hover:text-green-900 text-xs">Convert</button>
                                    <button onclick="event.stopPropagation(); app.leads.disqualifyLead(${lead.id})" 
                                            class="text-rose-600 hover:text-rose-800 text-xs">Disqualify</button>
                                    <button onclick="event.stopPropagation(); app.leads.assignLead(${lead.id})" 
                                            class="text-blue-600 hover:text-blue-800 text-xs">Assign</button>
                                    <button onclick="event.stopPropagation(); app.leads.editLead(${lead.id})" 
                                            class="text-yellow-600 hover:text-yellow-900 text-xs">Edit</button>
                                    <button onclick="event.stopPropagation(); app.leads.deleteLead(${lead.id})" 
                                            class="text-red-600 hover:text-red-900 text-xs">Delete</button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            document.getElementById('leads-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading leads</div>';
        }
    }

    getInitials(firstName, lastName) {
        return `${(firstName || '').charAt(0)}${(lastName || '').charAt(0)}`.toUpperCase();
    }

    searchLeads(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadLeadsList(term, document.getElementById('lead-status-filter').value);
        }, 300);
    }

    filterByStatus(status) {
        this.loadLeadsList(document.getElementById('lead-search').value, status);
    }

    showLeadForm(leadId = null) {
        const isEdit = leadId !== null;
        const title = isEdit ? 'Edit Lead' : 'Add New Lead';

        const modal = document.createElement('div');
        modal.id = 'lead-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('lead-modal').remove()" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="lead-form" class="p-6 space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                            <input type="text" id="first_name" name="first_name" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                        <div>
                            <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input type="text" id="last_name" name="last_name"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input type="email" id="email" name="email"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                        <div>
                            <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                            <input type="tel" id="phone" name="phone"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="company_name" class="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                            <input type="text" id="company_name" name="company_name"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                        <div>
                            <label for="website" class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                            <input type="url" id="website" name="website"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea id="description" name="description" rows="3"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"></textarea>
                    </div>
                    
                    <div class="flex items-center space-x-6">
                        <div class="flex items-center">
                            <input type="checkbox" id="disqualified" name="disqualified"
                                   class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded">
                            <label for="disqualified" class="ml-2 block text-sm text-gray-900">Disqualified</label>
                        </div>
                        <div class="flex items-center">
                            <input type="checkbox" id="was_in_touch" name="was_in_touch"
                                   class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded">
                            <label for="was_in_touch" class="ml-2 block text-sm text-gray-900">Was in touch</label>
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="document.getElementById('lead-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90">
                            ${isEdit ? 'Update' : 'Create'} Lead
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        if (isEdit) {
            this.loadLeadData(leadId);
        }

        document.getElementById('lead-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveLead(leadId);
        });
    }

    async loadLeadData(leadId) {
        try {
            const lead = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/`);
            
            const fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'website', 'description'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && lead[field]) {
                    element.value = lead[field];
                }
            });

            document.getElementById('disqualified').checked = lead.disqualified;
            document.getElementById('was_in_touch').checked = lead.was_in_touch;

        } catch (error) {
            this.app.showToast('Error loading lead data', 'error');
        }
    }

    async saveLead(leadId = null) {
        const formData = new FormData(document.getElementById('lead-form'));
        const leadData = Object.fromEntries(formData.entries());
        
        leadData.disqualified = document.getElementById('disqualified').checked;
        leadData.was_in_touch = document.getElementById('was_in_touch').checked;

        try {
            const method = leadId ? 'PUT' : 'POST';
            const url = leadId ? `${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/` : window.CRM_CONFIG.ENDPOINTS.LEADS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(leadData)
            });

            document.getElementById('lead-modal').remove();
            this.loadLeadsList();
            this.app.showToast(`Lead ${leadId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${leadId ? 'updating' : 'creating'} lead`, 'error');
        }
    }

    async editLead(leadId) {
        this.showLeadForm(leadId);
    }

    async deleteLead(leadId) {
        if (!confirm('Are you sure you want to delete this lead?')) {
            return;
        }

        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/`);
            this.loadLeadsList();
            this.app.showToast('Lead deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting lead', 'error');
        }
    }

    async convertToContact(leadId) {
        if (!confirm('Convert this lead to a contact? This will create a new contact record.')) {
            return;
        }

        try {
            const lead = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/`);
            
            // Create contact from lead data
            const contactData = {
                first_name: lead.first_name,
                last_name: lead.last_name,
                email: lead.email,
                phone: lead.phone,
                description: lead.description,
                // If lead has company_name, we could create a company first
                // For now, we'll just add it to description
            };

            if (lead.company_name) {
                contactData.description = (contactData.description || '') + `\nCompany: ${lead.company_name}`;
            }

            await window.apiClient.post(window.CRM_CONFIG.ENDPOINTS.CONTACTS, contactData);

            // Mark lead as converted (you might want to add a field for this)
            await window.apiClient.patch(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/`, { disqualified: true });

            this.app.showToast('Lead converted to contact successfully', 'success');
            this.loadLeadsList();
            return res;
        } catch (e) {
            this.app.showToast('Convert failed', 'error');
        }
    }

    async viewLead(leadId) {
        try {
            const lead = await this.app.apiCall(`/v1/leads/${leadId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'lead-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Lead Details</h3>
                            <button onclick="document.getElementById('lead-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                <div class="h-20 w-20 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white text-2xl font-bold">
                                    ${this.getInitials(lead.first_name, lead.last_name)}
                                </div>
                            </div>
                            
                            <div class="flex-1">
                                <div class="flex items-center justify-between">
                                    <h4 class="text-2xl font-bold text-gray-900">${lead.full_name}</h4>
                                    <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${lead.disqualified ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
                                        ${lead.disqualified ? 'Disqualified' : 'Active'}
                                    </span>
                                </div>
                                
                                ${lead.company_name ? `<p class="text-lg text-gray-600 mt-1">${lead.company_name}</p>` : ''}
                                
                                <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <dl class="space-y-3">
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Email</dt>
                                                <dd class="text-sm text-gray-900">${lead.email || 'No email'}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Phone</dt>
                                                <dd class="text-sm text-gray-900">${lead.phone || 'No phone'}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Website</dt>
                                                <dd class="text-sm text-gray-900">${lead.website ? `<a href="${lead.website}" target="_blank" class="text-primary-600 hover:text-primary-800">${lead.website}</a>` : 'No website'}</dd>
                                            </div>
                                        </dl>
                                    </div>
                                    
                                    <div>
                                        <dl class="space-y-3">
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Contact Status</dt>
                                                <dd class="text-sm">
                                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${lead.was_in_touch ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                                        ${lead.was_in_touch ? 'Contacted' : 'Not Contacted'}
                                                    </span>
                                                </dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Created</dt>
                                                <dd class="text-sm text-gray-900">${new Date(lead.creation_date).toLocaleDateString()}</dd>
                                            </div>
                                            <div>
                                                <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                                <dd class="text-sm text-gray-900">${new Date(lead.update_date).toLocaleDateString()}</dd>
                                            </div>
                                        </dl>
                                    </div>
                                </div>
                                
                                ${lead.description ? `
                                    <div class="mt-6">
                                        <h5 class="text-lg font-medium text-gray-900 mb-3">Description</h5>
                                        <p class="text-gray-700">${lead.description}</p>
                                    </div>
                                ` : ''}
                                
                                <div class="mt-8 flex justify-end space-x-3">
                                    ${!lead.disqualified ? `
                                        <button onclick="app.leads.convertToContact(${lead.id}); document.getElementById('lead-view-modal').remove();" 
                                                class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600">
                                            Convert to Contact
                                        </button>
                                    ` : ''}
                                    <button onclick="app.leads.editLead(${lead.id}); document.getElementById('lead-view-modal').remove();" 
                                            class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                                        Edit Lead
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading lead details', 'error');
        }
    }

    toggleSelected(id, checked) {
        if (checked) this.selected.add(id); else this.selected.delete(id);
        const el = document.getElementById('leads-selected-count');
        if (el) el.textContent = this.selected.size;
    }

    // Dialogs
    makeModal(contentHTML) {
        const wrap = document.createElement('div');
        wrap.innerHTML = `
        <div class="fixed inset-0 z-50 flex items-center justify-center">
            <div class="absolute inset-0 bg-black bg-opacity-40" onclick="this.parentElement.remove()"></div>
            <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md p-5">${contentHTML}</div>
        </div>`;
        return wrap.firstElementChild;
    }

    openBulkAssignDialog() {
        if (!this.selected.size) return this.app.showToast('Nothing selected','warning');
        const modal = this.makeModal(`
            <h3 class="text-lg font-semibold mb-3">Bulk Assign</h3>
            <input id="bulk-owner" type="number" placeholder="User ID" class="w-full border rounded px-3 py-2 mb-4"/>
            <div class="flex justify-end space-x-2">
                <button class="px-3 py-1 bg-gray-200 rounded" onclick="this.closest('.fixed').remove()">Cancel</button>
                <button class="px-3 py-1 bg-blue-600 text-white rounded" onclick="app.leads.bulkAssign()">Assign</button>
            </div>`);
        document.body.appendChild(modal);
    }

    async bulkAssign() {
        const owner = Number(document.getElementById('bulk-owner').value);
        if (!owner) return this.app.showToast('Enter user id','error');
        for (const id of this.selected) {
            await this.app.apiCall(`/v1/leads/${id}/assign/`, { method:'POST', body: JSON.stringify({ owner }) });
        }
        document.querySelector('.fixed.inset-0')?.remove();
        this.app.showToast('Assigned','success');
        this.loadLeadsList();
    }

    openBulkTagDialog() {
        if (!this.selected.size) return this.app.showToast('Nothing selected','warning');
        const modal = this.makeModal(`
            <h3 class="text-lg font-semibold mb-3">Bulk Tag</h3>
            <input id="bulk-tags" type="text" placeholder="Tag IDs comma-separated" class="w-full border rounded px-3 py-2 mb-4"/>
            <div class="flex justify-end space-x-2">
                <button class="px-3 py-1 bg-gray-200 rounded" onclick="this.closest('.fixed').remove()">Cancel</button>
                <button class="px-3 py-1 bg-indigo-600 text-white rounded" onclick="app.leads.bulkTag()">Apply</button>
            </div>`);
        document.body.appendChild(modal);
    }

    async bulkTag() {
        const raw = document.getElementById('bulk-tags').value;
        const tags = raw.split(',').map(s=>Number(s.trim())).filter(Boolean);
        await this.app.apiCall('/v1/leads/bulk-tag/', { method:'POST', body: JSON.stringify({ ids: Array.from(this.selected), tags }) });
        document.querySelector('.fixed.inset-0')?.remove();
        this.app.showToast('Tags added','success');
        this.loadLeadsList();
    }

    openBulkDisqualifyDialog() {
        if (!this.selected.size) return this.app.showToast('Nothing selected','warning');
        const modal = this.makeModal(`
            <h3 class="text-lg font-semibold mb-3">Bulk Disqualify</h3>
            <textarea id="bulk-reason" class="w-full border rounded px-3 py-2 mb-4" placeholder="Reason"></textarea>
            <div class="flex justify-end space-x-2">
                <button class="px-3 py-1 bg-gray-200 rounded" onclick="this.closest('.fixed').remove()">Cancel</button>
                <button class="px-3 py-1 bg-rose-600 text-white rounded" onclick="app.leads.bulkDisqualify()">Disqualify</button>
            </div>`);
        document.body.appendChild(modal);
    }

    async bulkDisqualify() {
        const reason = document.getElementById('bulk-reason').value || '';
        for (const id of this.selected) {
            await this.app.apiCall(`/v1/leads/${id}/disqualify/`, { method:'POST', body: JSON.stringify({ reason }) });
        }
        document.querySelector('.fixed.inset-0')?.remove();
        this.app.showToast('Leads disqualified','success');
        this.loadLeadsList();
    }

    // Actions
    async convertLead(leadId) {
        try {
            const withDeal = window.confirm('Create deal as well?');
            const res = await this.app.apiCall(`/v1/leads/${leadId}/convert/`, {
                method: 'POST',
                body: JSON.stringify({ create_deal: withDeal })
            });
            this.app.showToast('Lead converted', 'success');
            this.loadLeadsList();
            return res;
        } catch (e) {
            this.app.showToast('Convert failed', 'error');
        }
    }

    async disqualifyLead(leadId) {
        try {
            const reason = await this.prompt('Reason of disqualification:');
            const res = await window.apiClient.post(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/disqualify/`, { reason });
            this.app.showToast('Lead disqualified', 'success');
            this.loadLeadsList();
            return res;
        } catch (e) {
            if (e.message !== 'cancelled') this.app.showToast('Disqualify failed', 'error');
        }
    }

    async assignLead(leadId) {
        try {
            const owner = await this.prompt('Assign to user id:');
            const res = await window.apiClient.post(`${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/assign/`, { owner: Number(owner) });
            this.app.showToast('Lead assigned', 'success');
            this.loadLeadsList();
            return res;
        } catch (e) {
            if (e.message !== 'cancelled') this.app.showToast('Assign failed', 'error');
        }
    }
}
