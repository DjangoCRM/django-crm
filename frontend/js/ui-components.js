// Advanced UI Components Library for CRM System

class CRMUIComponents {
    constructor() {
        this.modals = new Map();
        this.tables = new Map();
        this.forms = new Map();
        this.init();
    }

    init() {
        this.setupGlobalStyles();
        this.setupEventListeners();
    }

    setupGlobalStyles() {
        // Add custom CSS for components
        const style = document.createElement('style');
        style.textContent = `
            .crm-modal {
                backdrop-filter: blur(8px);
                animation: fadeIn 0.2s ease-out;
            }
            .crm-modal-content {
                animation: slideIn 0.3s ease-out;
                transform-origin: center top;
            }
            .crm-table {
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .crm-table thead th {
                position: sticky;
                top: 0;
                background: white;
                z-index: 10;
            }
            .crm-form-field {
                transition: all 0.2s ease;
            }
            .crm-form-field:focus-within {
                transform: translateY(-1px);
            }
            .crm-button {
                transition: all 0.2s ease;
            }
            .crm-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .crm-badge {
                display: inline-flex;
                align-items: center;
                font-size: 0.75rem;
                font-weight: 500;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
            }
            .crm-badge-success { background: #dcfce7; color: #166534; }
            .crm-badge-warning { background: #fef3c7; color: #92400e; }
            .crm-badge-error { background: #fecaca; color: #991b1b; }
            .crm-badge-info { background: #dbeafe; color: #1e40af; }
            .crm-badge-primary { background: #e0e7ff; color: #3730a3; }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from { opacity: 0; transform: scale(0.9) translateY(-20px); }
                to { opacity: 1; transform: scale(1) translateY(0); }
            }
            .fade-enter { animation: fadeIn 0.2s ease-out; }
            .fade-exit { animation: fadeOut 0.2s ease-out; }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Global escape key handler for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });
    }

    // Modal Components
    createModal(id, options = {}) {
        const modal = {
            id,
            element: null,
            options: {
                title: options.title || 'Modal',
                size: options.size || 'md', // sm, md, lg, xl, full
                closable: options.closable !== false,
                backdrop: options.backdrop !== false,
                footer: options.footer !== false,
                ...options
            }
        };

        modal.element = this.buildModalElement(modal);
        this.modals.set(id, modal);
        return modal;
    }

    buildModalElement(modal) {
        const { id, options } = modal;
        const sizeClasses = {
            sm: 'max-w-md',
            md: 'max-w-lg', 
            lg: 'max-w-2xl',
            xl: 'max-w-4xl',
            full: 'max-w-7xl'
        };

        const modalHtml = `
            <div id="${id}" class="crm-modal fixed inset-0 bg-black bg-opacity-50 hidden z-50 flex items-center justify-center p-4">
                <div class="crm-modal-content bg-white rounded-lg shadow-xl ${sizeClasses[options.size]} w-full max-h-[90vh] overflow-hidden">
                    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-semibold text-gray-900" id="${id}-title">${options.title}</h3>
                        ${options.closable ? `
                            <button type="button" class="text-gray-400 hover:text-gray-600 transition-colors" onclick="window.crmUI.closeModal('${id}')">
                                <i class="fas fa-times text-lg"></i>
                            </button>
                        ` : ''}
                    </div>
                    <div class="px-6 py-4 overflow-y-auto" id="${id}-body">
                        <!-- Modal content will be inserted here -->
                    </div>
                    ${options.footer ? `
                        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3" id="${id}-footer">
                            <!-- Footer buttons will be inserted here -->
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        const div = document.createElement('div');
        div.innerHTML = modalHtml;
        const modalElement = div.firstElementChild;
        document.body.appendChild(modalElement);

        // Add backdrop click handler
        if (options.backdrop && options.closable) {
            modalElement.addEventListener('click', (e) => {
                if (e.target === modalElement) {
                    this.closeModal(id);
                }
            });
        }

        return modalElement;
    }

    openModal(id, content = '', footerButtons = []) {
        const modal = this.modals.get(id);
        if (!modal) {
            console.error(`Modal ${id} not found`);
            return;
        }

        // Set content
        const bodyElement = document.getElementById(`${id}-body`);
        if (typeof content === 'string') {
            bodyElement.innerHTML = content;
        } else if (content instanceof HTMLElement) {
            bodyElement.innerHTML = '';
            bodyElement.appendChild(content);
        }

        // Set footer buttons
        if (modal.options.footer && footerButtons.length > 0) {
            const footerElement = document.getElementById(`${id}-footer`);
            footerElement.innerHTML = '';
            
            footerButtons.forEach(button => {
                const btn = document.createElement('button');
                btn.className = `crm-button px-4 py-2 rounded-lg font-medium transition-colors ${button.class || 'bg-gray-500 hover:bg-gray-600 text-white'}`;
                btn.textContent = button.text;
                if (button.icon) {
                    btn.innerHTML = `<i class="${button.icon} mr-2"></i>${button.text}`;
                }
                btn.addEventListener('click', button.onclick || (() => this.closeModal(id)));
                footerElement.appendChild(btn);
            });
        }

        // Show modal
        modal.element.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Focus management
        const firstInput = modal.element.querySelector('input, select, textarea, button');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    closeModal(id) {
        const modal = this.modals.get(id);
        if (!modal) return;

        modal.element.classList.add('hidden');
        
        // Check if any modals are still open
        const openModals = Array.from(this.modals.values()).some(m => !m.element.classList.contains('hidden'));
        if (!openModals) {
            document.body.style.overflow = '';
        }
    }

    closeTopModal() {
        // Close the topmost modal
        const openModals = Array.from(this.modals.values())
            .filter(m => !m.element.classList.contains('hidden'))
            .sort((a, b) => {
                const aZIndex = parseInt(getComputedStyle(a.element).zIndex) || 0;
                const bZIndex = parseInt(getComputedStyle(b.element).zIndex) || 0;
                return bZIndex - aZIndex;
            });

        if (openModals.length > 0 && openModals[0].options.closable) {
            this.closeModal(openModals[0].id);
        }
    }

    updateModalTitle(id, title) {
        const titleElement = document.getElementById(`${id}-title`);
        if (titleElement) {
            titleElement.textContent = title;
        }
    }

    // Form Components
    createForm(id, config = {}) {
        const form = {
            id,
            config: {
                fields: config.fields || [],
                validation: config.validation || {},
                onSubmit: config.onSubmit || (() => {}),
                submitText: config.submitText || 'Submit',
                cancelText: config.cancelText || 'Cancel',
                layout: config.layout || 'vertical', // vertical, horizontal, grid
                ...config
            },
            data: {},
            errors: {}
        };

        form.element = this.buildFormElement(form);
        this.forms.set(id, form);
        return form;
    }

    buildFormElement(form) {
        const { id, config } = form;
        const layoutClass = config.layout === 'grid' ? 'grid grid-cols-2 gap-4' : 'space-y-4';
        
        let formHtml = `
            <form id="${id}" class="crm-form ${layoutClass}" novalidate>
        `;

        config.fields.forEach(field => {
            formHtml += this.buildFormField(field, id);
        });

        if (config.showButtons !== false) {
            formHtml += `
                <div class="flex justify-end space-x-3 pt-4 ${config.layout === 'grid' ? 'col-span-2' : ''}">
                    ${config.showCancel !== false ? `
                        <button type="button" class="crm-button px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg">
                            ${config.cancelText}
                        </button>
                    ` : ''}
                    <button type="submit" class="crm-button px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg">
                        <i class="fas fa-save mr-2"></i>${config.submitText}
                    </button>
                </div>
            `;
        }

        formHtml += '</form>';

        const div = document.createElement('div');
        div.innerHTML = formHtml;
        const formElement = div.firstElementChild;

        // Add event listeners
        formElement.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm(id);
        });

        // Cancel button handler
        const cancelBtn = formElement.querySelector('button[type="button"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                if (config.onCancel) {
                    config.onCancel();
                } else {
                    this.resetForm(id);
                }
            });
        }

        return formElement;
    }

    buildFormField(field, formId) {
        const fieldId = `${formId}_${field.name}`;
        const required = field.required ? 'required' : '';
        const placeholder = field.placeholder || '';
        
        let fieldHtml = `
            <div class="crm-form-field">
                <label for="${fieldId}" class="block text-sm font-medium text-gray-700 mb-2">
                    ${field.label}
                    ${field.required ? '<span class="text-red-500">*</span>' : ''}
                </label>
        `;

        switch (field.type) {
            case 'select':
                fieldHtml += `
                    <select id="${fieldId}" name="${field.name}" ${required}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        <option value="">${placeholder || 'Select an option'}</option>
                `;
                if (field.options) {
                    field.options.forEach(option => {
                        const value = typeof option === 'object' ? option.value : option;
                        const label = typeof option === 'object' ? option.label : option;
                        fieldHtml += `<option value="${value}">${label}</option>`;
                    });
                }
                fieldHtml += '</select>';
                break;

            case 'textarea':
                fieldHtml += `
                    <textarea id="${fieldId}" name="${field.name}" ${required} rows="${field.rows || 3}"
                              placeholder="${placeholder}"
                              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                `;
                break;

            case 'checkbox':
                fieldHtml = `
                    <div class="crm-form-field flex items-center">
                        <input type="checkbox" id="${fieldId}" name="${field.name}" ${required}
                               class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500">
                        <label for="${fieldId}" class="ml-2 text-sm text-gray-700">
                            ${field.label}
                            ${field.required ? '<span class="text-red-500">*</span>' : ''}
                        </label>
                `;
                break;

            case 'radio':
                fieldHtml += '<div class="space-y-2">';
                if (field.options) {
                    field.options.forEach(option => {
                        const value = typeof option === 'object' ? option.value : option;
                        const label = typeof option === 'object' ? option.label : option;
                        fieldHtml += `
                            <div class="flex items-center">
                                <input type="radio" id="${fieldId}_${value}" name="${field.name}" value="${value}" ${required}
                                       class="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500">
                                <label for="${fieldId}_${value}" class="ml-2 text-sm text-gray-700">${label}</label>
                            </div>
                        `;
                    });
                }
                fieldHtml += '</div>';
                break;

            case 'file':
                fieldHtml += `
                    <input type="file" id="${fieldId}" name="${field.name}" ${required}
                           accept="${field.accept || ''}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                `;
                break;

            case 'date':
            case 'email':
            case 'tel':
            case 'password':
            case 'number':
                fieldHtml += `
                    <input type="${field.type}" id="${fieldId}" name="${field.name}" ${required}
                           placeholder="${placeholder}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                `;
                break;

            default: // text
                fieldHtml += `
                    <input type="text" id="${fieldId}" name="${field.name}" ${required}
                           placeholder="${placeholder}"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                `;
        }

        if (field.help) {
            fieldHtml += `<p class="mt-1 text-sm text-gray-500">${field.help}</p>`;
        }

        fieldHtml += '<div class="error-message text-red-500 text-sm mt-1 hidden"></div>';
        fieldHtml += '</div>';

        return fieldHtml;
    }

    // Form data management
    setFormData(id, data) {
        const form = this.forms.get(id);
        if (!form) return;

        Object.entries(data).forEach(([key, value]) => {
            const field = form.element.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = Boolean(value);
                } else if (field.type === 'radio') {
                    const radio = form.element.querySelector(`[name="${key}"][value="${value}"]`);
                    if (radio) radio.checked = true;
                } else {
                    field.value = value || '';
                }
            }
        });

        form.data = { ...data };
    }

    getFormData(id) {
        const form = this.forms.get(id);
        if (!form) return {};

        const formData = new FormData(form.element);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Handle checkboxes that might not be in FormData
        form.element.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            if (!data.hasOwnProperty(checkbox.name)) {
                data[checkbox.name] = checkbox.checked;
            }
        });

        return data;
    }

    validateForm(id) {
        const form = this.forms.get(id);
        if (!form) return false;

        const data = this.getFormData(id);
        const errors = {};

        // Clear previous errors
        form.element.querySelectorAll('.error-message').forEach(el => {
            el.classList.add('hidden');
            el.textContent = '';
        });
        form.element.querySelectorAll('.border-red-500').forEach(el => {
            el.classList.remove('border-red-500');
            el.classList.add('border-gray-300');
        });

        // Validate each field
        form.config.fields.forEach(field => {
            const value = data[field.name];
            const fieldElement = form.element.querySelector(`[name="${field.name}"]`);

            // Required validation
            if (field.required && (!value || value.toString().trim() === '')) {
                errors[field.name] = 'This field is required';
            }

            // Email validation
            if (field.type === 'email' && value && !/\S+@\S+\.\S+/.test(value)) {
                errors[field.name] = 'Please enter a valid email address';
            }

            // Custom validation
            if (form.config.validation[field.name] && value) {
                const customError = form.config.validation[field.name](value, data);
                if (customError) {
                    errors[field.name] = customError;
                }
            }

            // Show error if exists
            if (errors[field.name] && fieldElement) {
                fieldElement.classList.add('border-red-500');
                fieldElement.classList.remove('border-gray-300');
                
                const errorDiv = fieldElement.parentNode.querySelector('.error-message');
                if (errorDiv) {
                    errorDiv.textContent = errors[field.name];
                    errorDiv.classList.remove('hidden');
                }
            }
        });

        form.errors = errors;
        return Object.keys(errors).length === 0;
    }

    submitForm(id) {
        const form = this.forms.get(id);
        if (!form) return;

        if (this.validateForm(id)) {
            const data = this.getFormData(id);
            form.config.onSubmit(data, form);
        }
    }

    resetForm(id) {
        const form = this.forms.get(id);
        if (!form) return;

        form.element.reset();
        form.data = {};
        form.errors = {};

        // Clear errors
        form.element.querySelectorAll('.error-message').forEach(el => {
            el.classList.add('hidden');
            el.textContent = '';
        });
        form.element.querySelectorAll('.border-red-500').forEach(el => {
            el.classList.remove('border-red-500');
            el.classList.add('border-gray-300');
        });
    }

    // Badge component
    createBadge(text, type = 'primary', icon = null) {
        const badge = document.createElement('span');
        badge.className = `crm-badge crm-badge-${type}`;
        
        if (icon) {
            badge.innerHTML = `<i class="${icon} mr-1"></i>${text}`;
        } else {
            badge.textContent = text;
        }
        
        return badge;
    }

    // Table Components
    createTable(id, config = {}) {
        const table = {
            id,
            config: {
                columns: config.columns || [],
                data: config.data || [],
                sortable: config.sortable !== false,
                filterable: config.filterable !== false,
                paginated: config.paginated !== false,
                pageSize: config.pageSize || 10,
                actions: config.actions || [],
                onRowClick: config.onRowClick || null,
                onSort: config.onSort || null,
                onFilter: config.onFilter || null,
                onPageChange: config.onPageChange || null,
                emptyText: config.emptyText || 'No data found',
                loadingText: config.loadingText || 'Loading...',
                ...config
            },
            currentPage: 1,
            sortColumn: null,
            sortDirection: 'asc',
            filters: {},
            filteredData: [],
            isLoading: false
        };

        table.element = this.buildTableElement(table);
        this.tables.set(id, table);
        this.updateTable(id);
        return table;
    }

    buildTableElement(table) {
        const { id, config } = table;
        
        let tableHtml = `
            <div id="${id}" class="crm-table bg-white border border-gray-200 rounded-lg overflow-hidden">
                <!-- Table Header with Search and Actions -->
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold text-gray-900" id="${id}-title">
                            ${config.title || 'Data Table'}
                        </h3>
                        <div class="flex items-center space-x-3">
                            ${config.filterable ? `
                                <div class="relative">
                                    <input type="text" id="${id}-search" placeholder="Search..."
                                           class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <i class="fas fa-search text-gray-400"></i>
                                    </div>
                                </div>
                            ` : ''}
                            ${config.actions.map(action => `
                                <button type="button" class="crm-button px-4 py-2 ${action.class || 'bg-primary-600 hover:bg-primary-700 text-white'} rounded-lg"
                                        data-action="${action.name}">
                                    ${action.icon ? `<i class="${action.icon} mr-2"></i>` : ''}
                                    ${action.text}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Table Content -->
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr id="${id}-header">
                                <!-- Headers will be generated dynamically -->
                            </tr>
                        </thead>
                        <tbody id="${id}-body" class="bg-white divide-y divide-gray-200">
                            <!-- Rows will be generated dynamically -->
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                ${config.paginated ? `
                    <div class="px-6 py-4 bg-gray-50 border-t border-gray-200">
                        <div class="flex items-center justify-between">
                            <div class="text-sm text-gray-700">
                                Showing <span id="${id}-showing-start">0</span> to <span id="${id}-showing-end">0</span> 
                                of <span id="${id}-total-count">0</span> results
                            </div>
                            <div class="flex items-center space-x-2" id="${id}-pagination">
                                <!-- Pagination buttons will be generated -->
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        const div = document.createElement('div');
        div.innerHTML = tableHtml;
        const tableElement = div.firstElementChild;

        // Add event listeners
        this.setupTableEventListeners(table, tableElement);

        return tableElement;
    }

    setupTableEventListeners(table, tableElement) {
        const { id, config } = table;

        // Search functionality
        if (config.filterable) {
            const searchInput = tableElement.querySelector(`#${id}-search`);
            searchInput.addEventListener('input', (e) => {
                this.filterTable(id, e.target.value);
            });
        }

        // Action buttons
        config.actions.forEach(action => {
            const btn = tableElement.querySelector(`[data-action="${action.name}"]`);
            if (btn) {
                btn.addEventListener('click', () => {
                    if (action.onClick) {
                        action.onClick(this.getSelectedRows(id));
                    }
                });
            }
        });
    }

    updateTable(id, newData = null) {
        const table = this.tables.get(id);
        if (!table) return;

        if (newData !== null) {
            table.config.data = newData;
        }

        if (table.isLoading) {
            this.showTableLoading(id);
            return;
        }

        this.applyFiltersAndSort(id);
        this.renderTableHeader(id);
        this.renderTableBody(id);
        if (table.config.paginated) {
            this.renderPagination(id);
        }
    }

    renderTableHeader(id) {
        const table = this.tables.get(id);
        if (!table) return;

        const headerRow = document.getElementById(`${id}-header`);
        headerRow.innerHTML = '';

        table.config.columns.forEach(column => {
            const th = document.createElement('th');
            th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
            
            if (table.config.sortable && column.sortable !== false) {
                th.className += ' cursor-pointer hover:bg-gray-100';
                th.innerHTML = `
                    <div class="flex items-center space-x-1">
                        <span>${column.title}</span>
                        <i class="fas fa-sort text-gray-400 ${table.sortColumn === column.key ? 
                            (table.sortDirection === 'asc' ? 'fa-sort-up text-primary-600' : 'fa-sort-down text-primary-600') 
                            : ''}"></i>
                    </div>
                `;
                
                th.addEventListener('click', () => {
                    this.sortTable(id, column.key);
                });
            } else {
                th.textContent = column.title;
            }

            headerRow.appendChild(th);
        });

        // Actions column
        if (table.config.rowActions && table.config.rowActions.length > 0) {
            const actionTh = document.createElement('th');
            actionTh.className = 'px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider';
            actionTh.textContent = 'Actions';
            headerRow.appendChild(actionTh);
        }
    }

    renderTableBody(id) {
        const table = this.tables.get(id);
        if (!table) return;

        const tbody = document.getElementById(`${id}-body`);
        tbody.innerHTML = '';

        if (table.filteredData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="${table.config.columns.length + (table.config.rowActions ? 1 : 0)}" 
                        class="px-6 py-12 text-center text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-4 block text-gray-400"></i>
                        ${table.config.emptyText}
                    </td>
                </tr>
            `;
            return;
        }

        const startIndex = table.config.paginated ? (table.currentPage - 1) * table.config.pageSize : 0;
        const endIndex = table.config.paginated ? startIndex + table.config.pageSize : table.filteredData.length;
        const pageData = table.filteredData.slice(startIndex, endIndex);

        pageData.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 cursor-pointer';
            tr.dataset.index = startIndex + index;

            // Add row click handler
            if (table.config.onRowClick) {
                tr.addEventListener('click', (e) => {
                    if (!e.target.closest('button')) { // Don't trigger if clicking action buttons
                        table.config.onRowClick(row, startIndex + index);
                    }
                });
            }

            // Render data columns
            table.config.columns.forEach(column => {
                const td = document.createElement('td');
                td.className = 'px-6 py-4 whitespace-nowrap text-sm';
                
                let cellContent = this.getCellValue(row, column.key);
                
                if (column.render) {
                    cellContent = column.render(cellContent, row, startIndex + index);
                } else if (column.type === 'badge') {
                    const badgeType = column.badgeMap?.[cellContent] || 'primary';
                    cellContent = this.createBadge(cellContent, badgeType).outerHTML;
                } else if (column.type === 'date') {
                    cellContent = cellContent ? new Date(cellContent).toLocaleDateString() : '';
                } else if (column.type === 'currency') {
                    cellContent = cellContent ? `$${Number(cellContent).toLocaleString()}` : '$0';
                }

                if (typeof cellContent === 'string') {
                    td.innerHTML = cellContent;
                } else if (cellContent instanceof HTMLElement) {
                    td.appendChild(cellContent);
                } else {
                    td.textContent = cellContent || '';
                }

                tr.appendChild(td);
            });

            // Render action buttons
            if (table.config.rowActions && table.config.rowActions.length > 0) {
                const actionTd = document.createElement('td');
                actionTd.className = 'px-6 py-4 whitespace-nowrap text-right text-sm font-medium';
                
                const actionContainer = document.createElement('div');
                actionContainer.className = 'flex items-center justify-end space-x-2';

                table.config.rowActions.forEach(action => {
                    if (!action.condition || action.condition(row)) {
                        const button = document.createElement('button');
                        button.className = `text-${action.color || 'primary'}-600 hover:text-${action.color || 'primary'}-900`;
                        button.innerHTML = `<i class="${action.icon}"></i>`;
                        button.title = action.title || action.name;
                        button.addEventListener('click', (e) => {
                            e.stopPropagation();
                            if (action.onClick) {
                                action.onClick(row, startIndex + index);
                            }
                        });
                        actionContainer.appendChild(button);
                    }
                });

                actionTd.appendChild(actionContainer);
                tr.appendChild(actionTd);
            }

            tbody.appendChild(tr);
        });
    }

    renderPagination(id) {
        const table = this.tables.get(id);
        if (!table) return;

        const totalItems = table.filteredData.length;
        const totalPages = Math.ceil(totalItems / table.config.pageSize);
        const startItem = (table.currentPage - 1) * table.config.pageSize + 1;
        const endItem = Math.min(table.currentPage * table.config.pageSize, totalItems);

        // Update count display
        document.getElementById(`${id}-showing-start`).textContent = totalItems > 0 ? startItem : 0;
        document.getElementById(`${id}-showing-end`).textContent = endItem;
        document.getElementById(`${id}-total-count`).textContent = totalItems;

        // Render pagination buttons
        const paginationContainer = document.getElementById(`${id}-pagination`);
        paginationContainer.innerHTML = '';

        if (totalPages <= 1) return;

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = `px-3 py-2 text-sm bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 ${table.currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}`;
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.disabled = table.currentPage === 1;
        prevBtn.addEventListener('click', () => this.changePage(id, table.currentPage - 1));
        paginationContainer.appendChild(prevBtn);

        // Page numbers
        const maxVisiblePages = 5;
        const startPage = Math.max(1, table.currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `px-3 py-2 text-sm border-t border-b border-r border-gray-300 ${
                i === table.currentPage 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'bg-white hover:bg-gray-50 text-gray-700'
            }`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => this.changePage(id, i));
            paginationContainer.appendChild(pageBtn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = `px-3 py-2 text-sm bg-white border-t border-r border-b border-gray-300 rounded-r-md hover:bg-gray-50 ${table.currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}`;
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.disabled = table.currentPage === totalPages;
        nextBtn.addEventListener('click', () => this.changePage(id, table.currentPage + 1));
        paginationContainer.appendChild(nextBtn);
    }

    getCellValue(row, key) {
        return key.split('.').reduce((obj, prop) => obj?.[prop], row);
    }

    applyFiltersAndSort(id) {
        const table = this.tables.get(id);
        if (!table) return;

        let data = [...table.config.data];

        // Apply global search filter
        if (table.searchQuery) {
            data = data.filter(row => {
                return table.config.columns.some(column => {
                    const value = this.getCellValue(row, column.key);
                    return value && value.toString().toLowerCase().includes(table.searchQuery.toLowerCase());
                });
            });
        }

        // Apply custom filters
        Object.entries(table.filters).forEach(([key, value]) => {
            if (value) {
                data = data.filter(row => {
                    const cellValue = this.getCellValue(row, key);
                    return cellValue && cellValue.toString().toLowerCase().includes(value.toLowerCase());
                });
            }
        });

        // Apply sorting
        if (table.sortColumn) {
            data.sort((a, b) => {
                const aVal = this.getCellValue(a, table.sortColumn) || '';
                const bVal = this.getCellValue(b, table.sortColumn) || '';
                
                let result = 0;
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    result = aVal - bVal;
                } else {
                    result = aVal.toString().localeCompare(bVal.toString());
                }
                
                return table.sortDirection === 'desc' ? -result : result;
            });
        }

        table.filteredData = data;
        
        // Reset to first page if data changed significantly
        if (table.currentPage > Math.ceil(data.length / table.config.pageSize)) {
            table.currentPage = 1;
        }
    }

    sortTable(id, column) {
        const table = this.tables.get(id);
        if (!table) return;

        if (table.sortColumn === column) {
            table.sortDirection = table.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            table.sortColumn = column;
            table.sortDirection = 'asc';
        }

        if (table.config.onSort) {
            table.config.onSort(column, table.sortDirection);
        } else {
            this.updateTable(id);
        }
    }

    filterTable(id, query) {
        const table = this.tables.get(id);
        if (!table) return;

        table.searchQuery = query;
        table.currentPage = 1;

        if (table.config.onFilter) {
            table.config.onFilter(query);
        } else {
            this.updateTable(id);
        }
    }

    changePage(id, page) {
        const table = this.tables.get(id);
        if (!table) return;

        table.currentPage = page;

        if (table.config.onPageChange) {
            table.config.onPageChange(page);
        } else {
            this.updateTable(id);
        }
    }

    setTableLoading(id, loading = true) {
        const table = this.tables.get(id);
        if (!table) return;

        table.isLoading = loading;
        this.updateTable(id);
    }

    showTableLoading(id) {
        const table = this.tables.get(id);
        if (!table) return;

        const tbody = document.getElementById(`${id}-body`);
        tbody.innerHTML = `
            <tr>
                <td colspan="${table.config.columns.length + (table.config.rowActions ? 1 : 0)}" 
                    class="px-6 py-12 text-center">
                    <div class="flex items-center justify-center">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div>
                        <span class="text-gray-600">${table.config.loadingText}</span>
                    </div>
                </td>
            </tr>
        `;
    }

    getSelectedRows(id) {
        // This would be implemented for row selection functionality
        return [];
    }

    // Utility functions
    showLoading(element, text = 'Loading...') {
        element.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div>
                <span class="text-gray-600">${text}</span>
            </div>
        `;
    }

    showEmpty(element, text = 'No data found', icon = 'fas fa-inbox') {
        element.innerHTML = `
            <div class="text-center py-12">
                <i class="${icon} text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600">${text}</p>
            </div>
        `;
    }
}

// Initialize global UI components
window.crmUI = new CRMUIComponents();