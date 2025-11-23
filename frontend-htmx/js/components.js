// UI Components Library

class ComponentManager {
    constructor() {
        this.modals = new Map();
        this.toastContainer = null;
        this.initToastContainer();
    }

    // Initialize toast container
    initToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'fixed top-4 right-4 space-y-2 z-50';
        this.toastContainer.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 2000;
            display: flex;
            flex-direction: column;
            gap: 8px;
        `;
        document.body.appendChild(this.toastContainer);
    }

    // Show toast notification
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
        `;

        // Add close handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.removeToast(toast));

        this.toastContainer.appendChild(toast);

        // Show with animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.removeToast(toast), duration);
        }

        return toast;
    }

    // Remove toast
    removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Create modal
    createModal(id, options = {}) {
        const {
            title = 'Modal',
            content = '',
            size = 'medium',
            closable = true,
            footer = null
        } = options;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = id;

        const sizeClasses = {
            small: 'w-96',
            medium: 'w-[600px]',
            large: 'w-[800px]',
            full: 'w-[90vw]'
        };

        modal.innerHTML = `
            <div class="modal-container ${sizeClasses[size]}">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    ${closable ? '<button class="modal-close">×</button>' : ''}
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
            </div>
        `;

        document.body.appendChild(modal);
        this.modals.set(id, modal);

        // Add event listeners
        if (closable) {
            const closeBtn = modal.querySelector('.modal-close');
            closeBtn?.addEventListener('click', () => this.closeModal(id));
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(id);
                }
            });
        }

        return modal;
    }

    // Show modal
    showModal(id) {
        const modal = this.modals.get(id);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    // Close modal
    closeModal(id) {
        const modal = this.modals.get(id);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Remove modal
    removeModal(id) {
        const modal = this.modals.get(id);
        if (modal) {
            modal.remove();
            this.modals.delete(id);
            document.body.style.overflow = '';
        }
    }

    // Create form
    createForm(fields, options = {}) {
        const {
            id = 'form',
            className = 'form-container',
            columns = 1,
            submitText = 'Submit',
            cancelText = 'Cancel',
            onSubmit = null,
            onCancel = null
        } = options;

        const form = document.createElement('form');
        form.id = id;
        form.className = className;

        const gridClass = columns > 1 ? 'form-grid' : '';
        const fieldsContainer = document.createElement('div');
        fieldsContainer.className = gridClass;

        fields.forEach(field => {
            const fieldElement = this.createFormField(field);
            fieldsContainer.appendChild(fieldElement);
        });

        form.appendChild(fieldsContainer);

        // Add actions
        const actions = document.createElement('div');
        actions.className = 'form-actions';

        if (onCancel) {
            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'btn btn-secondary';
            cancelBtn.textContent = cancelText;
            cancelBtn.addEventListener('click', onCancel);
            actions.appendChild(cancelBtn);
        }

        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = submitText;
        actions.appendChild(submitBtn);

        form.appendChild(actions);

        if (onSubmit) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                onSubmit(data);
            });
        }

        return form;
    }

    // Create form field
    createFormField(field) {
        const {
            type = 'text',
            name,
            label,
            placeholder = '',
            required = false,
            value = '',
            options = [],
            help = '',
            error = ''
        } = field;

        const group = document.createElement('div');
        group.className = 'form-group';

        // Label
        if (label) {
            const labelEl = document.createElement('label');
            labelEl.className = `form-label ${required ? 'required' : ''}`;
            labelEl.textContent = label;
            labelEl.setAttribute('for', name);
            group.appendChild(labelEl);
        }

        // Input
        let input;
        if (type === 'select') {
            input = document.createElement('select');
            input.className = 'form-input form-select';
            options.forEach(option => {
                const optionEl = document.createElement('option');
                optionEl.value = option.value || option;
                optionEl.textContent = option.label || option;
                if (value === optionEl.value) {
                    optionEl.selected = true;
                }
                input.appendChild(optionEl);
            });
        } else if (type === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'form-input form-textarea';
            input.value = value;
        } else if (type === 'checkbox') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'form-checkbox';
            input.checked = value;
        } else if (type === 'radio') {
            const radioGroup = document.createElement('div');
            radioGroup.className = 'flex gap-md';
            options.forEach(option => {
                const radioWrapper = document.createElement('label');
                radioWrapper.className = 'flex items-center gap-sm cursor-pointer';
                
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = name;
                radio.value = option.value || option;
                radio.className = 'form-radio';
                radio.checked = value === radio.value;
                
                const radioLabel = document.createElement('span');
                radioLabel.textContent = option.label || option;
                
                radioWrapper.appendChild(radio);
                radioWrapper.appendChild(radioLabel);
                radioGroup.appendChild(radioWrapper);
            });
            group.appendChild(radioGroup);
        } else {
            input = document.createElement('input');
            input.type = type;
            input.className = 'form-input';
            input.value = value;
        }

        if (input && type !== 'radio') {
            input.name = name;
            input.id = name;
            if (placeholder) input.placeholder = placeholder;
            if (required) input.required = true;
            group.appendChild(input);
        }

        // Help text
        if (help) {
            const helpEl = document.createElement('div');
            helpEl.className = 'form-help';
            helpEl.textContent = help;
            group.appendChild(helpEl);
        }

        // Error message
        if (error) {
            const errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            errorEl.textContent = error;
            group.appendChild(errorEl);
        }

        return group;
    }

    // Create data table
    createTable(columns, data, options = {}) {
        const {
            id = 'table',
            title = '',
            searchable = false,
            sortable = false,
            paginated = false,
            pageSize = 10,
            emptyMessage = 'No data available',
            actions = []
        } = options;

        const container = document.createElement('div');
        container.className = 'table-container';

        // Header
        if (title || actions.length > 0) {
            const header = document.createElement('div');
            header.className = 'table-header';

            if (title) {
                const titleEl = document.createElement('h3');
                titleEl.className = 'table-title';
                titleEl.textContent = title;
                header.appendChild(titleEl);
            }

            if (actions.length > 0) {
                const actionsEl = document.createElement('div');
                actionsEl.className = 'table-actions';
                actions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = `btn ${action.type || 'btn-primary'}`;
                    btn.textContent = action.text;
                    if (action.onClick) {
                        btn.addEventListener('click', action.onClick);
                    }
                    actionsEl.appendChild(btn);
                });
                header.appendChild(actionsEl);
            }

            container.appendChild(header);
        }

        // Search
        if (searchable) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'table-filters';
            
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'form-input';
            searchInput.placeholder = 'Search...';
            searchInput.style.width = '300px';
            
            searchContainer.appendChild(searchInput);
            container.appendChild(searchContainer);
        }

        // Table wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'table-wrapper';

        // Table
        const table = document.createElement('table');
        table.className = 'data-table';
        table.id = id;

        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column.label || column.key;
            if (sortable && column.sortable !== false) {
                th.className = 'table-sort';
                th.addEventListener('click', () => {
                    // Sort logic would go here
                    console.log(`Sort by ${column.key}`);
                });
            }
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        
        if (data.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = columns.length;
            cell.className = 'text-center';
            cell.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <div class="empty-state-title">No Data</div>
                    <div class="empty-state-description">${emptyMessage}</div>
                </div>
            `;
            row.appendChild(cell);
            tbody.appendChild(row);
        } else {
            data.forEach(item => {
                const row = document.createElement('tr');
                columns.forEach(column => {
                    const cell = document.createElement('td');
                    
                    if (column.render) {
                        cell.innerHTML = column.render(item[column.key], item);
                    } else {
                        cell.textContent = item[column.key] || '';
                    }
                    
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });
        }
        
        table.appendChild(tbody);
        wrapper.appendChild(table);
        container.appendChild(wrapper);

        // Pagination
        if (paginated && data.length > 0) {
            const pagination = document.createElement('div');
            pagination.className = 'table-pagination';
            
            const info = document.createElement('div');
            info.className = 'pagination-info';
            info.textContent = `Showing 1-${Math.min(pageSize, data.length)} of ${data.length} results`;
            
            const controls = document.createElement('div');
            controls.className = 'pagination-controls';
            
            // Previous button
            const prevBtn = document.createElement('button');
            prevBtn.className = 'pagination-btn';
            prevBtn.textContent = 'Previous';
            prevBtn.disabled = true;
            
            // Page numbers would go here
            const pageBtn = document.createElement('button');
            pageBtn.className = 'pagination-btn active';
            pageBtn.textContent = '1';
            
            // Next button
            const nextBtn = document.createElement('button');
            nextBtn.className = 'pagination-btn';
            nextBtn.textContent = 'Next';
            nextBtn.disabled = data.length <= pageSize;
            
            controls.appendChild(prevBtn);
            controls.appendChild(pageBtn);
            controls.appendChild(nextBtn);
            
            pagination.appendChild(info);
            pagination.appendChild(controls);
            container.appendChild(pagination);
        }

        return container;
    }

    // Show loading state
    showLoading(element) {
        if (!element) return;
        
        element.classList.add('loading', 'relative');
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="flex items-center">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading...</div>
            </div>
        `;
        
        element.appendChild(overlay);
    }

    // Hide loading state
    hideLoading(element) {
        if (!element) return;
        
        element.classList.remove('loading');
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Create dropdown
    createDropdown(trigger, items, options = {}) {
        const {
            position = 'bottom-left',
            className = ''
        } = options;

        const dropdown = document.createElement('div');
        dropdown.className = `dropdown ${className}`;

        // Menu
        const menu = document.createElement('div');
        menu.className = 'dropdown-menu';

        items.forEach(item => {
            if (item.divider) {
                const divider = document.createElement('div');
                divider.className = 'dropdown-divider';
                menu.appendChild(divider);
            } else {
                const menuItem = document.createElement('a');
                menuItem.className = 'dropdown-item';
                menuItem.href = item.href || '#';
                menuItem.innerHTML = `
                    ${item.icon ? `<span>${item.icon}</span>` : ''}
                    <span>${item.text}</span>
                `;
                
                if (item.onClick) {
                    menuItem.addEventListener('click', (e) => {
                        e.preventDefault();
                        item.onClick();
                        dropdown.classList.remove('active');
                    });
                }
                
                menu.appendChild(menuItem);
            }
        });

        // Toggle functionality
        trigger.addEventListener('click', () => {
            dropdown.classList.toggle('active');
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        dropdown.appendChild(trigger);
        dropdown.appendChild(menu);

        return dropdown;
    }
}

// Export singleton
window.componentManager = new ComponentManager();