// Deal management functionality
class DealManager {
    selected = new Set();
    restoreSelection(){ try{ this.selected=new Set(JSON.parse(localStorage.getItem('deals_selected')||'[]')); }catch{ this.selected=new Set(); } }
    saveSelection(){ localStorage.setItem('deals_selected', JSON.stringify(Array.from(this.selected))); }
    toggleSelected(id, checked){ if(checked) this.selected.add(id); else this.selected.delete(id); this.saveSelection(); const el=document.getElementById('deals-selected-count'); if(el) el.textContent=this.selected.size; }
    constructor(app) {
        this.app = app;
    }

    async loadDeals() {
        this.kanban = false;
        const section = document.getElementById('deals-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Deals</h2>
                        <div class="flex space-x-2">
                            <select id="deal-stage-filter" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                                <option value="">All Stages</option>
                            </select>
                            <input type="text" id="deal-search" placeholder="Search deals..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                            <button onclick="app.deals.showDealForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                                Add Deal
                            </button>
                        </div>
                    </div>
                </div>
                <div class="px-6 py-2 border-t border-gray-100 bg-gray-50 flex items-center justify-between">
                   <div class="flex items-center space-x-2">
                       <button id="deals-list-btn" class="px-3 py-1.5 rounded bg-primary-600 text-white text-sm">List</button>
                       <button id="deals-kanban-btn" class="px-3 py-1.5 rounded bg-gray-200 text-sm">Kanban</button>
                   </div>
                   <div class="text-sm text-gray-500" id="deals-info"></div>
                </div>
                <div class=\"px-6 py-2 border-t border-gray-100 flex items-center justify-between\">
                    <div class=\"flex items-center gap-3\">
                      <label class=\"inline-flex items-center gap-2\"><input id=\"deals-select-all\" type=\"checkbox\" class=\"rounded\" /><span class=\"text-sm text-gray-600\">Select all</span></label>
                      <button onclick=\"app.deals.openBulkAssignDialog()\" class=\"px-3 py-1.5 bg-blue-600 text-white rounded text-sm\">Bulk Assign</button>
                      <button onclick=\"app.deals.openBulkTagDialog()\" class=\"px-3 py-1.5 bg-indigo-600 text-white rounded text-sm\">Bulk Tag</button>
                    </div>
                    <div class=\"text-sm text-gray-500\">Selected: <span id=\"deals-selected-count\">0</span></div>
                 </div>
                 <div id=\"deals-content\" class=\"p-6\">
                    <div class="htmx-indicator">Loading deals...</div>
                </div>
            </div>
        `;

        document.getElementById('deal-search').addEventListener('input', (e) => {
            this.searchDeals(e.target.value);
        });

        document.getElementById('deal-stage-filter').addEventListener('change', (e) => {
            this.filterByStage(e.target.value);
        });
        
        document.getElementById('deals-list-btn').addEventListener('click', ()=>{ this.kanban=false; this.loadDealsList(); });
        document.getElementById('deals-kanban-btn').addEventListener('click', ()=>{ this.kanban=true; this.loadKanban(); });
        document.getElementById('deals-select-all').addEventListener('change', (e)=>{
          const check=e.target.checked; document.querySelectorAll('#deals-content input[type="checkbox"][data-deal]').forEach(b=>{ b.checked=check; const id=Number(b.dataset.deal); if(id) this.toggleSelected(id, check); });
        });

        if (this.app.token) {
            this.loadStages();
            this.restoreSelection();
            this.loadDealsList();
        }
    }

    async loadStages() {
        try {
            const stages = await this.app.apiCall('/v1/stages/');
            const stageFilter = document.getElementById('deal-stage-filter');
            
            if (stages.results) {
                stages.results.forEach(stage => {
                    const option = document.createElement('option');
                    option.value = stage.id;
                    option.textContent = stage.name;
                    stageFilter.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading stages:', error);
        }
    }

    async loadDealsList(searchTerm = '', stageFilter = '') {
        // switch buttons state
        const listBtn = document.getElementById('deals-list-btn');
        const kbBtn = document.getElementById('deals-kanban-btn');
        if (listBtn && kbBtn) {
            listBtn.className = 'px-3 py-1.5 rounded ' + (this.kanban? 'bg-gray-200':'bg-primary-600 text-white');
            kbBtn.className   = 'px-3 py-1.5 rounded ' + (this.kanban? 'bg-primary-600 text-white':'bg-gray-200');
        }
        try {
            let url = '/deals/?';
            if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
            if (stageFilter) url += `stage=${stageFilter}&`;
            
            const deals = await this.app.apiCall(url);
            const content = document.getElementById('deals-content');
            
            if (!deals.results || deals.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            💼
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm || stageFilter ? 'No deals found for your criteria' : 'No deals found'}</p>
                        <button onclick="app.deals.showDealForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                            Add Your First Deal
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${deals.results.map(deal => `
                        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                             onclick="app.deals.viewDeal(${deal.id})">
                            <div class=\"flex items-start justify-between mb-3\">
                                <h3 class="text-lg font-medium text-gray-900 truncate">${deal.name}</h3>
                                <div class=\"flex items-center gap-2\">
                                    <span class=\"inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getStageColor(deal.stage_name)}\">${deal.stage_name || 'No stage'}</span>
                                    <input type=\"checkbox\" data-deal=\"${deal.id}\" ${this.selected.has(deal.id)?'checked':''} onclick=\"event.stopPropagation(); app.deals.toggleSelected(${deal.id}, this.checked)\" class=\"rounded\" />
                                </div>
                            </div>
                            
                            <div class="space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Amount:</span>
                                    <span class="text-sm font-medium text-gray-900">
                                        ${deal.amount ? `$${parseFloat(deal.amount).toLocaleString()}` : 'No amount'}
                                    </span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Probability:</span>
                                    <span class="text-sm font-medium text-gray-900">${deal.probability || 0}%</span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Company:</span>
                                    <span class="text-sm text-gray-900 truncate">${deal.company_name || 'No company'}</span>
                                </div>
                                
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-500">Next Step:</span>
                                    <span class="text-xs text-gray-500">${deal.next_step_date ? new Date(deal.next_step_date).toLocaleDateString() : 'No date'}</span>
                                </div>
                            </div>
                            
                            <div class="mt-4 flex justify-between items-center">
                                <div class="flex items-center space-x-2">
                                    <span class="inline-flex px-2 py-1 text-xs rounded-full ${deal.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                        ${deal.active ? 'Active' : 'Closed'}
                                    </span>
                                    ${deal.important ? '<span class="text-red-500">⭐</span>' : ''}
                                </div>
                                
                                <div class="flex space-x-1">
                                    <button onclick=\"event.stopPropagation(); app.deals.assignDeal(${deal.id})\" class=\"text-blue-600 hover:text-blue-900 text-xs\">Assign</button>
                                    <button onclick=\"event.stopPropagation(); app.deals.tagDeal(${deal.id})\" class=\"text-indigo-600 hover:text-indigo-900 text-xs\">Tag</button>
                                    <button onclick="event.stopPropagation(); app.deals.editDeal(${deal.id})" 
                                            class="text-yellow-600 hover:text-yellow-900 text-xs">Edit</button>
                                    <button onclick="event.stopPropagation(); app.deals.deleteDeal(${deal.id})" 
                                            class="text-red-600 hover:text-red-900 text-xs">Delete</button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${deals.count > deals.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-gray-500">
                            Showing ${deals.results.length} of ${deals.count} deals
                        </div>
                        <div class="flex space-x-2">
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Previous</button>
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;
        } catch (error) {
            document.getElementById('deals-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading deals</div>';
        }
    }

    getStageColor(stageName) {
        const stageColors = {
            'New': 'bg-blue-100 text-blue-800',
            'Qualified': 'bg-green-100 text-green-800',
            'Proposal': 'bg-yellow-100 text-yellow-800',
            'Negotiation': 'bg-orange-100 text-orange-800',
            'Closed Won': 'bg-green-100 text-green-800',
            'Closed Lost': 'bg-red-100 text-red-800'
        };
        return stageColors[stageName] || 'bg-gray-100 text-gray-800';
    }

    searchDeals(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadDealsList(term, document.getElementById('deal-stage-filter').value);
        }, 300);
    }

    filterByStage(stageId) {
        this.loadDealsList(document.getElementById('deal-search').value, stageId);
    }

    showDealForm(dealId = null) {
        const isEdit = dealId !== null;
        const title = isEdit ? 'Edit Deal' : 'Add New Deal';

        const modal = document.createElement('div');
        modal.id = 'deal-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('deal-modal').remove()" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="deal-form" class="p-6 space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="md:col-span-2">
                            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Deal Name *</label>
                            <input type="text" id="name" name="name" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        
                        <div>
                            <label for="amount" class="block text-sm font-medium text-gray-700 mb-1">Amount</label>
                            <input type="number" id="amount" name="amount" step="0.01"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        
                        <div>
                            <label for="probability" class="block text-sm font-medium text-gray-700 mb-1">Probability (%)</label>
                            <input type="number" id="probability" name="probability" min="0" max="100"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        
                        <div>
                            <label for="stage" class="block text-sm font-medium text-gray-700 mb-1">Stage</label>
                            <select id="stage" name="stage" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Stage</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="company" class="block text-sm font-medium text-gray-700 mb-1">Company</label>
                            <select id="company" name="company" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Company</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="contact" class="block text-sm font-medium text-gray-700 mb-1">Contact</label>
                            <select id="contact" name="contact" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Contact</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="next_step_date" class="block text-sm font-medium text-gray-700 mb-1">Next Step Date</label>
                            <input type="date" id="next_step_date" name="next_step_date"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                    </div>
                    
                    <div>
                        <label for="next_step" class="block text-sm font-medium text-gray-700 mb-1">Next Step</label>
                        <input type="text" id="next_step" name="next_step"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
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
                            <input type="checkbox" id="important" name="important"
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="important" class="ml-2 block text-sm text-gray-900">Important</label>
                        </div>
                        <div class="flex items-center">
                            <input type="checkbox" id="relevant" name="relevant" checked
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="relevant" class="ml-2 block text-sm text-gray-900">Relevant</label>
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="document.getElementById('deal-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                            ${isEdit ? 'Update' : 'Create'} Deal
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Load dropdowns
        this.loadDealFormDropdowns();

        if (isEdit) {
            this.loadDealData(dealId);
        }

        document.getElementById('deal-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDeal(dealId);
        });
    }

    async loadDealFormDropdowns() {
        try {
            const [stages, companies, contacts] = await Promise.all([
                this.app.apiCall('/v1/stages/'),
                this.app.apiCall('/v1/companies/'),
                this.app.apiCall('/v1/contacts/')
            ]);

            // Load stages
            const stageSelect = document.getElementById('stage');
            if (stages.results) {
                stages.results.forEach(stage => {
                    const option = document.createElement('option');
                    option.value = stage.id;
                    option.textContent = stage.name;
                    stageSelect.appendChild(option);
                });
            }

            // Load companies
            const companySelect = document.getElementById('company');
            if (companies.results) {
                companies.results.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.id;
                    option.textContent = company.full_name;
                    companySelect.appendChild(option);
                });
            }

            // Load contacts
            const contactSelect = document.getElementById('contact');
            if (contacts.results) {
                contacts.results.forEach(contact => {
                    const option = document.createElement('option');
                    option.value = contact.id;
                    option.textContent = contact.full_name;
                    contactSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading form dropdowns:', error);
        }
    }

    async loadDealData(dealId) {
        try {
            const deal = await this.app.apiCall(`/v1/deals/${dealId}/`);
            
            const fields = ['name', 'amount', 'probability', 'next_step', 'description', 'next_step_date'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && deal[field]) {
                    element.value = deal[field];
                }
            });

            // Set dropdowns
            if (deal.stage) document.getElementById('stage').value = deal.stage;
            if (deal.company) document.getElementById('company').value = deal.company;
            if (deal.contact) document.getElementById('contact').value = deal.contact;

            // Set checkboxes
            document.getElementById('active').checked = deal.active;
            document.getElementById('important').checked = deal.important;
            document.getElementById('relevant').checked = deal.relevant;

        } catch (error) {
            this.app.showToast('Error loading deal data', 'error');
        }
    }

    async saveDeal(dealId = null) {
        const formData = new FormData(document.getElementById('deal-form'));
        const dealData = Object.fromEntries(formData.entries());
        
        // Convert checkboxes to boolean
        dealData.active = document.getElementById('active').checked;
        dealData.important = document.getElementById('important').checked;
        dealData.relevant = document.getElementById('relevant').checked;
        
        // Remove empty fields
        Object.keys(dealData).forEach(key => {
            if (!dealData[key]) delete dealData[key];
        });

        try {
            const method = dealId ? 'PUT' : 'POST';
            const url = dealId ? `/v1/deals/${dealId}/` : '/v1/deals/';
            
            await this.app.apiCall(url, {
                method: method,
                body: JSON.stringify(dealData)
            });

            document.getElementById('deal-modal').remove();
            this.loadDealsList();
            this.app.showToast(`Deal ${dealId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${dealId ? 'updating' : 'creating'} deal`, 'error');
        }
    }

    async editDeal(dealId) {
        this.showDealForm(dealId);
    }

    async deleteDeal(dealId) {
        if (!confirm('Are you sure you want to delete this deal?')) {
            return;
        }

        try {
            await this.app.apiCall(`/v1/deals/${dealId}/`, { method: 'DELETE' });
            this.loadDealsList();
            this.app.showToast('Deal deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting deal', 'error');
        }
    }

    async viewDeal(dealId) {
        try {
            const deal = await this.app.apiCall(`/v1/deals/${dealId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'deal-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Deal Details</h3>
                            <button onclick="document.getElementById('deal-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
                                <span class="sr-only">Close</span>
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div class="p-6">
                        <div class="mb-6">
                            <div class="flex items-center justify-between">
                                <h4 class="text-2xl font-bold text-gray-900">${deal.name}</h4>
                                <div class="flex items-center space-x-2">
                                    <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${this.getStageColor(deal.stage_name)}">
                                        ${deal.stage_name || 'No stage'}
                                    </span>
                                    ${deal.important ? '<span class="text-red-500 text-xl">⭐</span>' : ''}
                                </div>
                            </div>
                            
                            ${deal.amount ? `
                                <div class="mt-2">
                                    <span class="text-3xl font-bold text-green-600">$${parseFloat(deal.amount).toLocaleString()}</span>
                                    <span class="text-gray-500 ml-2">(${deal.probability || 0}% probability)</span>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Deal Information</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Company</dt>
                                        <dd class="text-sm text-gray-900">${deal.company_name || 'No company'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Contact</dt>
                                        <dd class="text-sm text-gray-900">${deal.contact_name || 'No contact'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Next Step</dt>
                                        <dd class="text-sm text-gray-900">${deal.next_step || 'No next step'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Next Step Date</dt>
                                        <dd class="text-sm text-gray-900">${deal.next_step_date ? new Date(deal.next_step_date).toLocaleDateString() : 'No date set'}</dd>
                                    </div>
                                </dl>
                            </div>
                            
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Status & Dates</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Status</dt>
                                        <dd class="text-sm">
                                            <div class="flex items-center space-x-2">
                                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${deal.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                                    ${deal.active ? 'Active' : 'Closed'}
                                                </span>
                                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${deal.relevant ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}">
                                                    ${deal.relevant ? 'Relevant' : 'Not Relevant'}
                                                </span>
                                            </div>
                                        </dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Created</dt>
                                        <dd class="text-sm text-gray-900">${new Date(deal.creation_date).toLocaleDateString()}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                        <dd class="text-sm text-gray-900">${new Date(deal.update_date).toLocaleDateString()}</dd>
                                    </div>
                                    ${deal.closing_date ? `
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Closing Date</dt>
                                            <dd class="text-sm text-gray-900">${new Date(deal.closing_date).toLocaleDateString()}</dd>
                                        </div>
                                    ` : ''}
                                </dl>
                            </div>
                        </div>
                        
                        ${deal.description ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Description</h5>
                                <p class="text-gray-700">${deal.description}</p>
                            </div>
                        ` : ''}
                        
                        <div class="mt-8 flex justify-end space-x-3">
                            <button onclick="app.deals.editDeal(${deal.id}); document.getElementById('deal-view-modal').remove();" 
                                    class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                                Edit Deal
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading deal details', 'error');
        }
    }
}