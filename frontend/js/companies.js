// Company management functionality
class CompanyManager {
    constructor(app) {
        this.app = app;
    }

    async loadCompanies() {
        const section = document.getElementById('companies-section');
        section.innerHTML = ''; // Clear existing content

        const createEl = (tag, classes = '') => {
            const el = document.createElement(tag);
            if (classes) el.className = classes;
            return el;
        };

        const container = createEl('div', 'bg-white rounded-lg shadow dark:bg-slate-800');
        const header = createEl('div', 'px-6 py-4 border-b border-gray-200');
        const headerFlex = createEl('div', 'flex items-center justify-between');
        const h2 = createEl('h2', 'text-xl font-semibold text-gray-900');
        h2.textContent = 'Companies';
        
        const controlsDiv = createEl('div', 'flex space-x-2');
        const searchInput = createEl('input', 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary');
        searchInput.type = 'text';
        searchInput.id = 'company-search';
        searchInput.placeholder = 'Search companies...';
        
        const addButton = createEl('button', 'bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg');
        addButton.dataset.action = 'companies.showCompanyForm';
        addButton.textContent = 'Add Company';

        controlsDiv.append(searchInput, addButton);
        headerFlex.append(h2, controlsDiv);
        header.appendChild(headerFlex);

        const contentDiv = createEl('div', 'p-6');
        contentDiv.id = 'companies-content';
        contentDiv.appendChild(createEl('div', 'htmx-indicator'));
        
        container.append(header, contentDiv);
        section.appendChild(container);

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
            
            const modalContent = document.createElement('div');
            modalContent.className = 'bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800';

            // Header
            const header = document.createElement('div');
            header.className = 'px-6 py-4 border-b border-gray-200 flex items-center justify-between';
            const h3 = document.createElement('h3');
h3.className = 'text-lg font-medium text-gray-900';
            h3.textContent = 'Company Details';
            header.appendChild(h3);
            const closeButton = document.createElement('button');
            closeButton.dataset.action = 'companies.closeViewCompanyModal';
            closeButton.className = 'text-gray-400 hover:text-gray-600';
            closeButton.innerHTML = `<span class="sr-only">Close</span><svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>`;
            header.appendChild(closeButton);
            modalContent.appendChild(header);

            // Body
            const body = document.createElement('div');
            body.className = 'p-6';
            const bodyFlex = document.createElement('div');
            bodyFlex.className = 'flex items-start space-x-6';
            
            const avatarContainer = document.createElement('div');
            avatarContainer.className = 'flex-shrink-0';
            const avatar = document.createElement('div');
            avatar.className = 'h-20 w-20 rounded-lg bg-primary flex items-center justify-center text-white text-2xl font-bold';
            avatar.textContent = company.full_name.charAt(0).toUpperCase();
            avatarContainer.appendChild(avatar);
            bodyFlex.appendChild(avatarContainer);

            const mainContent = document.createElement('div');
            mainContent.className = 'flex-1';
            
            const nameH4 = document.createElement('h4');
            nameH4.className = 'text-xl font-bold text-gray-900';
            nameH4.textContent = company.full_name;
            mainContent.appendChild(nameH4);

            if (company.website) {
                const websiteLink = document.createElement('a');
                websiteLink.href = company.website;
                websiteLink.target = '_blank';
                websiteLink.className = 'text-primary hover:text-primary-800';
                websiteLink.textContent = company.website;
                mainContent.appendChild(websiteLink);
            }

            const grid = document.createElement('div');
            grid.className = 'mt-4 grid grid-cols-1 md:grid-cols-2 gap-6';

            const createDlEntry = (label, value) => {
                const div = document.createElement('div');
                const dt = document.createElement('dt');
                dt.className = 'text-sm font-medium text-gray-500';
                dt.textContent = label;
                div.appendChild(dt);
                const dd = document.createElement('dd');
                dd.className = 'text-sm text-gray-900';
                dd.textContent = value || 'N/A';
                div.appendChild(dd);
                return div;
            };

            const col1 = document.createElement('div');
            const dl1 = document.createElement('dl');
            dl1.className = 'space-y-3';
            dl1.appendChild(createDlEntry('Email', company.email));
            dl1.appendChild(createDlEntry('Phone', company.phone));
            dl1.appendChild(createDlEntry('Location', [company.city_name, company.country_name].filter(Boolean).join(', ')));
            col1.appendChild(dl1);
            grid.appendChild(col1);

            const col2 = document.createElement('div');
            const dl2 = document.createElement('dl');
            dl2.className = 'space-y-3';
            const statusDiv = document.createElement('div');
            const statusDt = document.createElement('dt');
            statusDt.className = 'text-sm font-medium text-gray-500';
            statusDt.textContent = 'Status';
            statusDiv.appendChild(statusDt);
            const statusDd = document.createElement('dd');
            statusDd.className = 'text-sm';
            const statusSpan = document.createElement('span');
            statusSpan.className = `inline-flex px-2 py-1 text-xs font-semibold rounded-full ${company.disqualified ? 'bg-danger bg-opacity-20 text-danger' : company.active ? 'bg-success bg-opacity-20 text-success' : 'bg-warning bg-opacity-20 text-warning'}`;
            statusSpan.textContent = company.disqualified ? 'Disqualified' : company.active ? 'Active' : 'Inactive';
            statusDd.appendChild(statusSpan);
            statusDiv.appendChild(statusDd);
            dl2.appendChild(statusDiv);
            dl2.appendChild(createDlEntry('Created', new Date(company.creation_date).toLocaleDateString()));
            dl2.appendChild(createDlEntry('Last Updated', new Date(company.update_date).toLocaleDateString()));
            col2.appendChild(dl2);
            grid.appendChild(col2);
            mainContent.appendChild(grid);

            if (company.address) mainContent.appendChild(createDlEntry('Address', company.address)).classList.add('mt-4');
            if (company.description) mainContent.appendChild(createDlEntry('Description', company.description)).classList.add('mt-4');
            
            const footer = document.createElement('div');
            footer.className = 'mt-6 flex justify-end space-x-3';
            const editButton = document.createElement('button');
            editButton.dataset.action = 'companies.editCompany';
            editButton.dataset.id = company.id;
            editButton.className = 'px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90';
            editButton.textContent = 'Edit Company';
            footer.appendChild(editButton);
            mainContent.appendChild(footer);

            bodyFlex.appendChild(mainContent);
            body.appendChild(bodyFlex);
            modalContent.appendChild(body);
            modal.appendChild(modalContent);

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
            
            content.innerHTML = ''; // Clear skeleton

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

            const grid = document.createElement('div');
            grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';
            companies.results.forEach(company => {
                grid.appendChild(this.renderCompanyCard(company));
            });
            content.appendChild(grid);
            
            if (companies.count > companies.results.length) {
                const pagination = document.createElement('div');
                pagination.className = 'mt-6 flex items-center justify-between';
                // This part is simple enough and doesn't contain user data, so innerHTML is acceptable here.
                pagination.innerHTML = `
                    <div class="text-sm text-surface-600">
                        Showing ${companies.results.length} of ${companies.count} companies
                    </div>
                    <div class="flex gap-2">
                        <button class="btn btn-secondary btn-sm">Previous</button>
                        <button class="btn btn-secondary btn-sm">Next</button>
                    </div>
                `;
                content.appendChild(pagination);
            }
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
        const createEl = (tag, classes = '', children = []) => {
            const el = document.createElement(tag);
            if (classes) el.className = classes;
            children.forEach(child => {
                if (typeof child === 'string') el.appendChild(document.createTextNode(child));
                else if (child) el.appendChild(child);
            });
            return el;
        };

        const card = createEl('div', 'card p-6 hover:shadow-medium transition-shadow');
        card.dataset.id = company.id;

        const header = createEl('div', 'flex items-start justify-between mb-4');
        const headerLeft = createEl('div', 'flex items-center gap-3');
        const avatar = createEl('div', 'avatar avatar-lg bg-primary-100', [
            createEl('span', 'text-primary-600 text-xl font-bold', [(company.full_name || '?').charAt(0).toUpperCase()])
        ]);
        const nameDiv = createEl('div');
        const nameH3 = createEl('h3', 'text-lg font-semibold text-surface-900');
        nameH3.textContent = company.full_name;
        nameDiv.appendChild(nameH3);

        if (company.website) {
            const websiteLink = createEl('a', 'text-sm text-primary-600 hover:underline');
            websiteLink.href = company.website;
            websiteLink.target = '_blank';
            websiteLink.textContent = company.website;
            nameDiv.appendChild(websiteLink);
        }
        headerLeft.append(avatar, nameDiv);
        header.appendChild(headerLeft);
        card.appendChild(header);

        const infoList = createEl('div', 'space-y-2 mb-4');
        const createInfoRow = (iconPath, text) => {
            if (!text) return null;
            const row = createEl('div', 'flex items-center gap-2 text-sm text-surface-700');
            const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            icon.setAttribute('class', 'w-4 h-4 text-surface-400');
            icon.setAttribute('fill', 'none');
            icon.setAttribute('stroke', 'currentColor');
            icon.setAttribute('viewBox', '0 0 24 24');
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('d', iconPath);
            icon.appendChild(path);
            row.appendChild(icon);
            row.appendChild(document.createTextNode(text));
            return row;
        };
        
        const emailRow = createInfoRow('M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z', company.email);
        if(emailRow) infoList.appendChild(emailRow);
        
        const phoneRow = createInfoRow('M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z', company.phone);
        if(phoneRow) infoList.appendChild(phoneRow);

        const cityRow = createInfoRow('M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z', company.city_name);
        if(cityRow) infoList.appendChild(cityRow);

        card.appendChild(infoList);

        const footer = createEl('div', 'flex gap-2 pt-4 border-t border-surface-200');
        const createButton = (action, id, text, classes, iconPath) => {
            const btn = createEl('button', `btn ${classes}`);
            btn.dataset.action = action;
            btn.dataset.id = id;
            if (iconPath) {
                const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                icon.setAttribute('class', 'w-4 h-4');
                icon.setAttribute('fill', 'none');
                icon.setAttribute('stroke', 'currentColor');
                icon.setAttribute('viewBox', '0 0 24 24');
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('stroke-linecap', 'round');
                path.setAttribute('stroke-linejoin', 'round');
                path.setAttribute('stroke-width', '2');
                path.setAttribute('d', iconPath);
                icon.appendChild(path);
                btn.appendChild(icon);
            }
            if (text) btn.appendChild(document.createTextNode(text));
            return btn;
        };
        footer.appendChild(createButton('companies.viewCompany', company.id, 'View', 'btn-secondary btn-sm flex-1'));
        footer.appendChild(createButton('companies.editCompany', company.id, null, 'btn-text btn-sm', 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'));
        footer.appendChild(createButton('companies.deleteCompany', company.id, null, 'btn-text btn-sm text-error-600', 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16'));
        card.appendChild(footer);

        return card;
    };

    CompanyManager.prototype.showCompanyForm = function(companyId = null) {
        const isEdit = companyId !== null;
        const title = isEdit ? 'Edit Company' : 'Add New Company';

        const createEl = (tag, classes = '', children = []) => {
            const el = document.createElement(tag);
            if (classes) el.className = classes;
            children.forEach(child => {
                if (typeof child === 'string') el.appendChild(document.createTextNode(child));
                else if (child) el.appendChild(child);
            });
            return el;
        };

        const createInputGroup = (id, label, input, hint = null) => {
            const labelEl = createEl('label', 'input-label', [label]);
            labelEl.htmlFor = id;
            const children = [labelEl, input];
            if (hint) children.push(createEl('p', 'input-hint', [hint]));
            return createEl('div', 'input-group', children);
        };

        const modal = createEl('div', 'modal-overlay fade-in');
        modal.id = 'company-modal';
        
        const dialogEl = createEl('div', 'modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100');
        dialogEl.setAttribute('aria-label', title);

        const form = createEl('form', 'modal-body space-y-4');
        form.id = 'company-form';

        form.appendChild(createInputGroup('full_name', 'Company Name *', Object.assign(createEl('input', 'input'), {type: 'text', id: 'full_name', name: 'full_name', required: true, placeholder: 'Acme Corporation'})));
        
        const grid1 = createEl('div', 'grid grid-cols-1 md:grid-cols-2 gap-4');
        grid1.appendChild(createInputGroup('email', 'Email', Object.assign(createEl('input', 'input'), {type: 'email', id: 'email', name: 'email', placeholder: 'info@company.com'}), 'Will be converted to lowercase'));
        grid1.appendChild(createInputGroup('phone', 'Phone', Object.assign(createEl('input', 'input'), {type: 'tel', id: 'phone', name: 'phone', placeholder: '+1234567890'}), 'Will be cleaned to +digits format'));
        form.appendChild(grid1);

        form.appendChild(createInputGroup('website', 'Website', Object.assign(createEl('input', 'input'), {type: 'url', id: 'website', name: 'website', placeholder: 'https://company.com'})));
        
        const textarea = createEl('textarea', 'input');
        textarea.id = 'description';
        textarea.name = 'description';
        textarea.rows = 3;
        form.appendChild(createInputGroup('description', 'Description', textarea));
        
        form.appendChild(createInputGroup('industry', 'Industry', Object.assign(createEl('input', 'input'), {type: 'text', id: 'industry', name: 'industry'}))).dataset.advanced = 'true';
        form.appendChild(createInputGroup('employees', 'Number of Employees', Object.assign(createEl('input', 'input'), {type: 'number', id: 'employees', name: 'employees'}))).dataset.advanced = 'true';

        dialogEl.append(
            createEl('div', 'modal-header', [
                createEl('h3', 'modal-title', [title]),
                (() => {
                    const btn = createEl('button', 'btn-icon btn-text');
                    btn.type = 'button';
                    btn.innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`;
                    btn.onclick = () => modal.remove();
                    return btn;
                })()
            ]),
            form,
            createEl('div', 'modal-footer', [
                (() => {
                    const btn = createEl('button', 'btn btn-secondary', ['Cancel']);
                    btn.type = 'button';
                    btn.onclick = () => modal.remove();
                    return btn;
                })(),
                (() => {
                    const btn = createEl('button', 'btn btn-primary');
                    btn.type = 'submit';
                    btn.setAttribute('form', 'company-form');
                    btn.innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> <span>${isEdit ? 'Update' : 'Create'} Company</span>`;
                    return btn;
                })()
            ])
        );
        modal.appendChild(dialogEl);
        document.body.appendChild(modal);
        
        document.body.style.overflow = 'hidden';
        const closeModal = () => {
            modal.remove();
            document.body.style.overflow = '';
            document.removeEventListener('keydown', onKeyDown);
        };
        const onKeyDown = (e) => { if (e.key === 'Escape') closeModal(); };
        document.addEventListener('keydown', onKeyDown);
        modal.addEventListener('click', (e) => { if (!dialogEl.contains(e.target)) closeModal(); });
        
        window.uxEnhancements?.applyFocusTrap(dialogEl);
        
        const companyForm = document.getElementById('company-form');

        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(companyForm);
        }

        if (!isEdit && window.uxEnhancements) {
            const defaults = window.uxEnhancements.getSmartDefaults('company', this.app.user?.id);
            window.uxEnhancements.applySmartDefaults(companyForm, defaults);
        }

        if (isEdit) {
            this.loadCompanyData(companyId);
        }

        companyForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCompany(companyId);
        });

        if (window.FormValidators) {
            window.FormValidators.setupFormNormalization(companyForm);
            window.FormValidators.setupFormValidation(companyForm);
        }

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
