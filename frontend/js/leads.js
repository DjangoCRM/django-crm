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
            <div class="bg-white rounded-lg shadow dark:bg-slate-800">
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
            let url = '/v1/leads/?'; // OK
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
                        <div class=\"bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\"
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
        const form = document.getElementById('lead-form');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Normalize booleans
        data.disqualified = document.getElementById('disqualified').checked;
        data.was_in_touch = document.getElementById('was_in_touch').checked;

        // Trim strings and clean empty values
        Object.keys(data).forEach(k => { if (typeof data[k] === 'string') data[k] = data[k].trim(); });
        if (!data.first_name && !data.company_name) {
            this.app.showToast('Enter at least First name or Company name', 'error');
            return;
        }
        Object.keys(data).forEach(k => { if (data[k] === '' || data[k] == null) delete data[k]; });

        try {
            const method = leadId ? 'PUT' : 'POST';
            const url = leadId ? `${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/` : window.CRM_CONFIG.ENDPOINTS.LEADS;
            await window.apiClient.request(url, { method, body: JSON.stringify(data) });
            document.getElementById('lead-modal')?.remove();
            this.loadLeadsList();
            this.app.showToast(`Lead ${leadId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            const msg = (error?.data && typeof error.data === 'object')
              ? Object.entries(error.data).map(([f, v]) => `${f}: ${Array.isArray(v)? v.join(', '): v}`).join('\n')
              : (error?.message || 'Bad Request');
            this.app.showToast(msg, 'error');
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
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
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
            <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md p-5 dark:bg-slate-800">${contentHTML}</div>
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
        // Step 1: select owner via typeahead
        try {
            await Typeahead.open({
                title:'Convert Lead', placeholder:'Search owner...', multiple:false,
                fetcher: async(q)=>{ const res=await this.app.apiCall(`/v1/users/?search=${encodeURIComponent(q||'')}`); return (res.results||res).map(u=>({id:u.id,name:u.first_name||u.username})) },
                onApply: async(ids)=>{
                    const owner = ids[0];
                    // Step 2: small modal to choose create_deal
                    const modal = this.makeModal(`
                        <h3 class='text-lg font-semibold mb-3'>Create Deal?</h3>
                        <label class='inline-flex items-center gap-2 mb-4'><input id='cv-create-deal' type='checkbox' class='rounded'/><span>Create deal along with conversion</span></label>
                        <div class='flex justify-end gap-2'>
                          <button class='px-3 py-1 bg-gray-200 rounded' onclick='this.closest(".fixed").remove()'>Cancel</button>
                          <button id='cv-apply' class='px-3 py-1 bg-green-600 text-white rounded'>Convert</button>
                        </div>`);
                    document.body.appendChild(modal);
                    modal.querySelector('#cv-apply').addEventListener('click', async ()=>{
                        const create_deal = !!modal.querySelector('#cv-create-deal').checked;
                        try {
                            const res = await this.app.apiCall(`/v1/leads/${leadId}/convert/`, { method:'POST', body: JSON.stringify({ owner, create_deal }) });
                            this.app.showToast('Lead converted', 'success');
                            this.loadLeadsList();
                        } catch(e){ this.app.showToast('Convert failed', 'error'); }
                        modal.remove();
                    });
                }
            });
        } catch (e) { /* closed */ }
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
        // typeahead select user
        try {
            await Typeahead.open({
                title:'Assign Lead', placeholder:'Search users...', multiple:false,
                fetcher: async(q)=>{ const res=await this.app.apiCall(`/v1/users/?search=${encodeURIComponent(q||'')}`); return (res.results||res).map(u=>({id:u.id,name:u.first_name||u.username})) },
                onApply: async(ids)=>{ const owner=ids[0]; if(!owner) return; await this.app.apiCall(`/v1/leads/${leadId}/assign/`, { method:'POST', body: JSON.stringify({ owner }) }); this.app.showToast('Lead assigned','success'); this.loadLeadsList(); }
            });
        } catch(e) { /* modal handles close */ }
        return;
    }
}

/* ===== Merged UX patches from leads-ux.js ===== */

/**
 * UX Enhancements for Leads Module
 */

if (typeof LeadManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadLeadsList with skeleton and empty states
    const originalLoadLeadsList = LeadManager.prototype.loadLeadsList;
    LeadManager.prototype.loadLeadsList = async function(searchTerm = '') {
        const content = document.getElementById('leads-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'list', 8);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const leads = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.LEADS}?${searchParam}`);
            
            if (!leads.results || leads.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '🎯',
                    title: searchTerm ? 'No leads found' : 'No leads yet',
                    description: searchTerm 
                        ? `No leads match "${searchTerm}"`
                        : 'Start capturing leads to grow your business',
                    actionLabel: 'Add Lead',
                    actionHandler: 'app.leads.showLeadForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("lead-search").value=""; app.leads.loadLeadsList()'
                    } : null
                });
                return;
            }

            // Render leads with status colors
            content.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 table-responsive">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    <input type="checkbox" id="select-all-leads" class="checkbox">
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class=\"bg-white divide-y divide-gray-200 dark:bg-slate-800 dark:divide-slate-700\">
                            ${leads.results.map(lead => `
                                <tr class="hover:bg-gray-50 dark:hover:bg-slate-700" data-id="${lead.id}">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="bulk-checkbox">
                                            <input type="checkbox" class="checkbox" value="${lead.id}">
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-full bg-warning-100 flex items-center justify-center text-warning-600 font-medium">
                                                    ${(lead.full_name || '?').charAt(0).toUpperCase()}
                                                </div>
                                            </div>
                                            <div class="ml-4">
                                                <div class="text-sm font-medium text-gray-900">${lead.full_name}</div>
                                                <div class="text-sm text-gray-500">${lead.title || ''}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${lead.company_name || 'No company'}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${lead.email || 'No email'}</div>
                                        <div class="text-sm text-gray-500">${lead.phone || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        ${this.renderLeadStatus(lead.status)}
                                    </td>
                                    text-gray-500 dark:text-slate-300'>
                                        ${lead.lead_source || 'Unknown'}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button data-action="leads.viewLead" data-id="${lead.id}" class="btn btn-text btn-sm">View</button>
                                            <button data-action="leads.editLead" data-id="${lead.id}" class="btn btn-text btn-sm">Edit</button>
                                            <button data-action="leads.convertLead" data-id="${lead.id}" class="btn btn-text btn-sm text-success-600">Convert</button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <!-- Mobile Card View -->
                <div class="card-view">
                    ${leads.results.map(lead => `
                        <div class="card-view-item" data-id="${lead.id}">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="bulk-checkbox">
                                    <input type="checkbox" class="checkbox" value="${lead.id}">
                                </div>
                                <div class="avatar avatar-md bg-warning-100">
                                    <span class="text-warning-600">${(lead.full_name || '?').charAt(0).toUpperCase()}</span>
                                </div>
                                <div class="flex-1">
                                    <h4 class="font-semibold">${lead.full_name}</h4>
                                    <p class="text-sm text-surface-600">${lead.company_name || ''}</p>
                                </div>
                                ${this.renderLeadStatus(lead.status)}
                            </div>
                            <div class="space-y-2">
                                ${lead.email ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Email</span>
                                        <span class="card-view-value">${lead.email}</span>
                                    </div>
                                ` : ''}
                                ${lead.phone ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Phone</span>
                                        <span class="card-view-value">${lead.phone}</span>
                                    </div>
                                ` : ''}
                                ${lead.lead_source ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Source</span>
                                        <span class="card-view-value">${lead.lead_source}</span>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="flex gap-2 mt-4 pt-4 border-t border-surface-200">
                                <button data-action="leads.viewLead" data-id="${lead.id}" class="btn btn-secondary btn-sm flex-1">View</button>
                                <button data-action="leads.editLead" data-id="${lead.id}" class="btn btn-secondary btn-sm flex-1">Edit</button>
                                <button data-action="leads.convertLead" data-id="${lead.id}" class="btn btn-primary btn-sm flex-1">Convert</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${leads.count > leads.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-surface-600">
                            Showing ${leads.results.length} of ${leads.count} leads
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-secondary btn-sm">Previous</button>
                            <button class="btn btn-secondary btn-sm">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;

            // Enable bulk selection
            if (window.advancedUX) {
                window.advancedUX.enableBulkSelection('#leads-content', '.bulk-checkbox');
            }

        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load leads',
                message: 'Unable to fetch leads from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.leads.loadLeadsList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Render lead status badge
    LeadManager.prototype.renderLeadStatus = function(status) {
        const statusConfig = {
            'new': { class: 'badge-primary', label: 'New' },
            'contacted': { class: 'badge-secondary', label: 'Contacted' },
            'qualified': { class: 'badge-success', label: 'Qualified' },
            'unqualified': { class: 'badge-error', label: 'Unqualified' },
            'converted': { class: 'badge-success', label: 'Converted' }
        };
        
        const config = statusConfig[status] || { class: 'badge-secondary', label: status || 'Unknown' };
        return `<span class="badge ${config.class}">${config.label}</span>`;
    };

    // Enhanced showLeadForm with smart defaults
    const originalShowLeadForm = LeadManager.prototype.showLeadForm;
    LeadManager.prototype.showLeadForm = function(leadId = null) {
        const isEdit = leadId !== null;
        const title = isEdit ? 'Edit Lead' : 'Add New Lead';

        const modal = document.createElement('div');
        modal.id = 'lead-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('lead-modal').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="lead-form" class="modal-body space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="first_name" class="input-label">First Name *</label>
                            <input type="text" id="first_name" name="first_name" required class="input">
                        </div>
                        <div class="input-group">
                            <label for="last_name" class="input-label">Last Name *</label>
                            <input type="text" id="last_name" name="last_name" required class="input">
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="company_name" class="input-label">Company Name</label>
                        <input type="text" id="company_name" name="company_name" class="input">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="email" class="input-label">Email *</label>
                            <input type="email" id="email" name="email" required class="input">
                            <p class="input-hint">Will be converted to lowercase</p>
                        </div>
                        <div class="input-group">
                            <label for="phone" class="input-label">Phone</label>
                            <input type="tel" id="phone" name="phone" class="input">
                            <p class="input-hint">Will be cleaned to +digits format</p>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="status" class="input-label">Status</label>
                            <select id="status" name="status" class="input select">
                                <option value="new">New</option>
                                <option value="contacted">Contacted</option>
                                <option value="qualified">Qualified</option>
                                <option value="unqualified">Unqualified</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label for="lead_source" class="input-label">Lead Source</label>
                            <select id="lead_source" name="lead_source" class="input select">
                                <option value="">Select source...</option>
                                <option value="website">Website</option>
                                <option value="referral">Referral</option>
                                <option value="social_media">Social Media</option>
                                <option value="email_campaign">Email Campaign</option>
                                <option value="trade_show">Trade Show</option>
                                <option value="cold_call">Cold Call</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <!-- Advanced fields -->
                    <div class="input-group" data-advanced="true">
                        <label for="title" class="input-label">Title</label>
                        <input type="text" id="title" name="title" class="input">
                    </div>
                    
                    <div class="input-group" data-advanced="true">
                        <label for="mobile" class="input-label">Mobile</label>
                        <input type="tel" id="mobile" name="mobile" class="input">
                    </div>
                    
                    <div class="input-group" data-advanced="true">
                        <label for="website" class="input-label">Website</label>
                        <input type="url" id="website" name="website" class="input">
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('lead-modal').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="lead-form" class="btn btn-primary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${isEdit ? 'Update' : 'Create'} Lead
                        ${!isEdit ? '<kbd class="ml-2">⌘S</kbd>' : ''}
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
        
        const leadForm = document.getElementById('lead-form');

        // Progressive disclosure
        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(leadForm);
        }

        // Smart defaults
        if (!isEdit && window.uxEnhancements) {
            const defaults = window.uxEnhancements.getSmartDefaults('lead', this.app.user?.id);
            window.uxEnhancements.applySmartDefaults(leadForm, defaults);
        }

        if (isEdit) {
            this.loadLeadData(leadId);
        }

        leadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveLead(leadId);
        });

        // Setup normalization and validation
        if (window.FormValidators) {
            window.FormValidators.setupFormNormalization(leadForm);
            window.FormValidators.setupFormValidation(leadForm);
        }

        setTimeout(() => document.getElementById('first_name').focus(), 100);
    };

    // Enhanced saveLead
    const originalSaveLead = LeadManager.prototype.saveLead;
    LeadManager.prototype.saveLead = async function(leadId = null) {
        const formData = new FormData(document.getElementById('lead-form'));
        const leadData = Object.fromEntries(formData.entries());
        
        // Remember values
        if (window.uxEnhancements && leadData.lead_source) {
            window.uxEnhancements.rememberValue('lead_source', leadData.lead_source);
        }

        try {
            const method = leadId ? 'PUT' : 'POST';
            const url = leadId 
                ? `${window.CRM_CONFIG.ENDPOINTS.LEADS}${leadId}/` 
                : window.CRM_CONFIG.ENDPOINTS.LEADS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(leadData)
            });

            document.getElementById('lead-modal').remove();
            this.loadLeadsList();
            this.app.showToast(
                `Lead ${leadId ? 'updated' : 'created'} successfully`, 
                'success'
            );
        } catch (error) {
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: `Failed to ${leadId ? 'update' : 'create'} lead`,
                    message: error.message || 'Please check your input and try again.',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: `app.leads.saveLead(${leadId})`, primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            } else {
                this.app.showToast(`Error ${leadId ? 'updating' : 'creating'} lead`, 'error');
            }
        }
    };

    // Setup search progress
    const originalLoadLeads = LeadManager.prototype.loadLeads;
    LeadManager.prototype.loadLeads = function() {
        originalLoadLeads.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('lead-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadLeadsList(term);
                });
            }
        }, 100);
    };
}
