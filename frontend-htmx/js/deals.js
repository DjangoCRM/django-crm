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
        section.innerHTML = ''; // Clear existing content

        const createEl = (tag, classes = '', children = []) => {
            const el = document.createElement(tag);
            if (classes) el.className = classes;
            children.forEach(child => {
                if (typeof child === 'string') el.appendChild(document.createTextNode(child));
                else if (child) el.appendChild(child);
            });
            return el;
        };

        const container = createEl('div', 'bg-white rounded-lg shadow dark:bg-slate-800');
        
        const headerDiv = createEl('div', 'px-6 py-4 border-b border-gray-200');
        const headerFlex = createEl('div', 'flex items-center justify-between');
        const h2 = createEl('h2', 'text-xl font-semibold text-gray-900', ['Deals']);
        
        const controlsDiv = createEl('div', 'flex space-x-2');
        const stageFilterSelect = createEl('select', 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500');
        stageFilterSelect.id = 'deal-stage-filter';
        const defaultOption = createEl('option', '', ['All Stages']);
        defaultOption.value = '';
        stageFilterSelect.appendChild(defaultOption);

        const searchInput = createEl('input', 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500');
        searchInput.type = 'text';
        searchInput.id = 'deal-search';
        searchInput.placeholder = 'Search deals...';
        
        const addButton = createEl('button', 'bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg', ['Add Deal']);
        addButton.onclick = () => this.showDealForm();

        controlsDiv.append(stageFilterSelect, searchInput, addButton);
        headerFlex.append(h2, controlsDiv);
        headerDiv.appendChild(headerFlex);
        container.appendChild(headerDiv);

        const viewToggleDiv = createEl('div', 'px-6 py-2 border-t border-gray-100 bg-gray-50 flex items-center justify-between');
        const viewToggleLeft = createEl('div', 'flex items-center space-x-2');
        const listBtn = createEl('button', 'px-3 py-1.5 rounded bg-primary-600 text-white text-sm', ['List']);
        listBtn.id = 'deals-list-btn';
        const kanbanBtn = createEl('button', 'px-3 py-1.5 rounded bg-gray-200 text-sm', ['Kanban']);
        kanbanBtn.id = 'deals-kanban-btn';
        viewToggleLeft.append(listBtn, kanbanBtn);
        const dealsInfoDiv = createEl('div', 'text-sm text-gray-500');
        dealsInfoDiv.id = 'deals-info';
        viewToggleDiv.append(viewToggleLeft, dealsInfoDiv);
        container.appendChild(viewToggleDiv);

        const bulkActionsDiv = createEl('div', 'px-6 py-2 border-t border-gray-100 flex items-center justify-between');
        const bulkLeft = createEl('div', 'flex items-center gap-3');
        const selectAllLabel = createEl('label', 'inline-flex items-center gap-2');
        const selectAllCheckbox = createEl('input', 'rounded');
        selectAllCheckbox.id = 'deals-select-all';
        selectAllCheckbox.type = 'checkbox';
        selectAllLabel.append(selectAllCheckbox, createEl('span', 'text-sm text-gray-600', ['Select all']));
        
        const bulkAssignBtn = createEl('button', 'px-3 py-1.5 bg-blue-600 text-white rounded text-sm', ['Bulk Assign']);
        bulkAssignBtn.onclick = () => this.openBulkAssignDialog();
        const bulkTagBtn = createEl('button', 'px-3 py-1.5 bg-indigo-600 text-white rounded text-sm', ['Bulk Tag']);
        bulkTagBtn.onclick = () => this.openBulkTagDialog();
        bulkLeft.append(selectAllLabel, bulkAssignBtn, bulkTagBtn);
        
        const selectedCountDiv = createEl('div', 'text-sm text-gray-500', ['Selected: ']);
        const selectedCountSpan = createEl('span', '', ['0']);
        selectedCountSpan.id = 'deals-selected-count';
        selectedCountDiv.appendChild(selectedCountSpan);
        bulkActionsDiv.append(bulkLeft, selectedCountDiv);
        container.appendChild(bulkActionsDiv);

        const contentDiv = createEl('div', 'p-6');
        contentDiv.id = 'deals-content';
        contentDiv.appendChild(createEl('div', 'htmx-indicator', ['Loading deals...']));
        container.appendChild(contentDiv);

        section.appendChild(container);

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
            const stages = await this.app.apiCall('/stages/');
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
                        <div class=\"bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\"
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



    async loadDealFormDropdowns() {
        try {
            const [stages, companies, contacts] = await Promise.all([
                this.app.apiCall('/stages/'),
                window.apiClient.get('/companies/'),
                window.apiClient.get('/contacts/')
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
            const deal = await this.app.apiCall(`/deals/${dealId}/`);
            
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
            const url = dealId ? `/deals/${dealId}/` : '/deals/';
            
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
            await this.app.apiCall(`/deals/${dealId}/`, { method: 'DELETE' });
            this.loadDealsList();
            this.app.showToast('Deal deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting deal', 'error');
        }
    }

    async viewDeal(dealId) {
        try {
            const deal = await this.app.apiCall(`/deals/${dealId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'deal-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
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
/* ===== Merged UX patches from deals-ux.js ===== */

/**
 * UX Enhancements for Deals Module
 */

if (typeof DealManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadDealsList with skeleton and empty states
    const originalLoadDealsList = DealManager.prototype.loadDealsList;
    DealManager.prototype.loadDealsList = async function(searchTerm = '') {
        const content = document.getElementById('deals-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'cards', 6);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const deals = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.DEALS}?${searchParam}`);
            
            if (!deals.results || deals.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '💰',
                    title: searchTerm ? 'No deals found' : 'No deals yet',
                    description: searchTerm 
                        ? `No deals match "${searchTerm}"`
                        : 'Start tracking deals to manage your pipeline',
                    actionLabel: 'Create Deal',
                    actionHandler: 'app.deals.showDealForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("deal-search").value=""; app.deals.loadDealsList()'
                    } : null
                });
                return;
            }

            // Group deals by stage for kanban view
            const dealsByStage = this.groupDealsByStage(deals.results);
            
            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    ${Object.entries(dealsByStage).map(([stage, stageDeals]) => `
                        <div class="bg-surface-100 rounded-xl p-4">
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="font-semibold text-surface-900">${this.formatStageName(stage)}</h3>
                                <span class="badge badge-secondary">${stageDeals.length}</span>
                            </div>
                            <div class="space-y-3">
                                ${stageDeals.map(deal => this.renderDealCard(deal)).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${deals.count > deals.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-surface-600">
                            Showing ${deals.results.length} of ${deals.count} deals
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
                title: 'Failed to load deals',
                message: 'Unable to fetch deals from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.deals.loadDealsList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Group deals by stage
    DealManager.prototype.groupDealsByStage = function(deals) {
        const stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
        const grouped = {};
        
        stages.forEach(stage => {
            grouped[stage] = deals.filter(deal => deal.stage === stage);
        });
        
        return grouped;
    };

    // Format stage name
    DealManager.prototype.formatStageName = function(stage) {
        const names = {
            'prospecting': '🔍 Prospecting',
            'qualification': '✅ Qualification',
            'proposal': '📄 Proposal',
            'negotiation': '🤝 Negotiation',
            'closed_won': '🎉 Closed Won',
            'closed_lost': '❌ Closed Lost'
        };
        return names[stage] || stage;
    };

    // Render deal card for kanban
    DealManager.prototype.renderDealCard = function(deal) {
        return `
            <div class="card p-4 cursor-pointer hover:shadow-medium transition-shadow" data-id="${deal.id}">
                <h4 class="font-semibold text-surface-900 mb-2">${deal.name}</h4>
                ${deal.company_name ? `<p class="text-sm text-surface-600 mb-2">${deal.company_name}</p>` : ''}
                <div class="flex items-center justify-between">
                    <span class="text-lg font-bold text-success-600">$${this.formatCurrency(deal.amount)}</span>
                    ${deal.close_date ? `<span class="text-xs text-surface-500">${this.formatDate(deal.close_date)}</span>` : ''}
                </div>
                <div class="flex gap-2 mt-3 pt-3 border-t border-surface-200">
                    <button data-action="deals.viewDeal" data-id="${deal.id}" class="btn btn-text btn-sm flex-1">View</button>
                    <button data-action="deals.editDeal" data-id="${deal.id}" class="btn btn-text btn-sm flex-1">Edit</button>
                </div>
            </div>
        `;
    };

    // Format currency
    DealManager.prototype.formatCurrency = function(amount) {
        return new Intl.NumberFormat('en-US', { 
            minimumFractionDigits: 0,
            maximumFractionDigits: 0 
        }).format(amount || 0);
    };

    // Format date
    DealManager.prototype.formatDate = function(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    };

    // Enhanced showDealForm
    const originalShowDealForm = DealManager.prototype.showDealForm;
    DealManager.prototype.showDealForm = function(dealId = null) {
        const isEdit = dealId !== null;
        const title = isEdit ? 'Edit Deal' : 'Create New Deal';

        const modal = document.createElement('div');
        modal.id = 'deal-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('deal-modal').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="deal-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <label for="name" class="input-label">Deal Name *</label>
                        <input type="text" id="name" name="name" required class="input" placeholder="Q4 Software License">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="amount" class="input-label">Amount *</label>
                            <input type="number" id="amount" name="amount" required class="input" placeholder="50000" step="0.01">
                        </div>
                        <div class="input-group">
                            <label for="close_date" class="input-label">Expected Close Date</label>
                            <input type="date" id="close_date" name="close_date" class="input">
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="stage" class="input-label">Stage *</label>
                            <select id="stage" name="stage" required class="input select">
                                <option value="prospecting">Prospecting</option>
                                <option value="qualification">Qualification</option>
                                <option value="proposal">Proposal</option>
                                <option value="negotiation">Negotiation</option>
                                <option value="closed_won">Closed Won</option>
                                <option value="closed_lost">Closed Lost</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label for="probability" class="input-label">Probability (%)</label>
                            <input type="number" id="probability" name="probability" class="input" min="0" max="100" placeholder="50">
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="company" class="input-label">Company</label>
                        <select id="company" name="company" class="input select">
                            <option value="">Select company...</option>
                        </select>
                    </div>
                    
                    <div class="input-group">
                        <label for="contact" class="input-label">Contact</label>
                        <select id="contact" name="contact" class="input select">
                            <option value="">Select contact...</option>
                        </select>
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <!-- Advanced fields -->
                    <div class="input-group" data-advanced="true">
                        <label for="lead_source" class="input-label">Lead Source</label>
                        <select id="lead_source" name="lead_source" class="input select">
                            <option value="">Select source...</option>
                            <option value="website">Website</option>
                            <option value="referral">Referral</option>
                            <option value="social_media">Social Media</option>
                            <option value="trade_show">Trade Show</option>
                        </select>
                    </div>
                    
                    <div class="input-group" data-advanced="true">
                        <label for="next_step" class="input-label">Next Step</label>
                        <input type="text" id="next_step" name="next_step" class="input">
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('deal-modal').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="deal-form" class="btn btn-primary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${isEdit ? 'Update' : 'Create'} Deal
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
        
        const dealForm = document.getElementById('deal-form');

        // Progressive disclosure
        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(dealForm);
        }

        // Smart defaults
        if (!isEdit && window.uxEnhancements) {
            const defaults = window.uxEnhancements.getSmartDefaults('deal', this.app.user?.id);
            // Set default close date to 30 days from now
            const closeDate = document.getElementById('close_date');
            if (closeDate && !closeDate.value) {
                const futureDate = new Date();
                futureDate.setDate(futureDate.getDate() + 30);
                closeDate.value = futureDate.toISOString().split('T')[0];
            }
            window.uxEnhancements.applySmartDefaults(dealForm, defaults);
        }

        // Load dropdowns
        this.loadCompaniesDropdown();
        this.loadContactsDropdown();

        if (isEdit) {
            this.loadDealData(dealId);
        }

        dealForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDeal(dealId);
        });

        setTimeout(() => document.getElementById('name').focus(), 100);
    };

    // Enhanced saveDeal
    const originalSaveDeal = DealManager.prototype.saveDeal;
    DealManager.prototype.saveDeal = async function(dealId = null) {
        const formData = new FormData(document.getElementById('deal-form'));
        const dealData = Object.fromEntries(formData.entries());

        try {
            const method = dealId ? 'PUT' : 'POST';
            const url = dealId 
                ? `${window.CRM_CONFIG.ENDPOINTS.DEALS}${dealId}/` 
                : window.CRM_CONFIG.ENDPOINTS.DEALS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(dealData)
            });

            document.getElementById('deal-modal').remove();
            this.loadDealsList();
            this.app.showToast(
                `Deal ${dealId ? 'updated' : 'created'} successfully`, 
                'success'
            );
        } catch (error) {
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: `Failed to ${dealId ? 'update' : 'create'} deal`,
                    message: error.message || 'Please check your input and try again.',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: `app.deals.saveDeal(${dealId})`, primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            } else {
                this.app.showToast(`Error ${dealId ? 'updating' : 'creating'} deal`, 'error');
            }
        }
    };

    // Setup search progress
    const originalLoadDeals = DealManager.prototype.loadDeals;
    DealManager.prototype.loadDeals = function() {
        originalLoadDeals.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('deal-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadDealsList(term);
                });
            }
        }, 100);
    };
}
