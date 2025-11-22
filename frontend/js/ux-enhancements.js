/**
 * UX Enhancements Module
 * Implements Quick Wins and critical UX improvements
 */

class UXEnhancements {
    constructor() {
        this.searchTimeouts = new Map();
        this.lastUsedValues = new Map();
        this.setupKeyboardShortcuts();
    }

    /**
     * 1. SKELETON SCREENS
     * Show skeleton loading instead of spinners
     */
    showSkeleton(container, type = 'list', count = 5) {
        const skeletons = {
            list: this.generateListSkeleton(count),
            cards: this.generateCardsSkeleton(count),
            table: this.generateTableSkeleton(count),
            form: this.generateFormSkeleton()
        };

        container.innerHTML = skeletons[type] || skeletons.list;
        container.classList.add('loading-skeleton');
    }

    generateListSkeleton(count) {
        return `
            <div class="space-y-4 animate-pulse">
                ${Array(count).fill().map(() => `
                    <div class="flex items-center gap-4 p-4 bg-white border border-surface-200 rounded-lg">
                        <div class="flex-shrink-0 w-12 h-12 bg-surface-200 rounded-full"></div>
                        <div class="flex-1 space-y-2">
                            <div class="h-4 bg-surface-200 rounded w-3/4"></div>
                            <div class="h-3 bg-surface-200 rounded w-1/2"></div>
                        </div>
                        <div class="flex gap-2">
                            <div class="w-8 h-8 bg-surface-200 rounded"></div>
                            <div class="w-8 h-8 bg-surface-200 rounded"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    generateCardsSkeleton(count) {
        return `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                ${Array(count).fill().map(() => `
                    <div class="card p-6 space-y-4">
                        <div class="flex items-center justify-between">
                            <div class="h-6 bg-surface-200 rounded w-2/3"></div>
                            <div class="w-16 h-6 bg-surface-200 rounded-full"></div>
                        </div>
                        <div class="space-y-2">
                            <div class="h-4 bg-surface-200 rounded"></div>
                            <div class="h-4 bg-surface-200 rounded w-5/6"></div>
                            <div class="h-4 bg-surface-200 rounded w-3/4"></div>
                        </div>
                        <div class="flex gap-2 pt-4">
                            <div class="h-8 bg-surface-200 rounded flex-1"></div>
                            <div class="h-8 bg-surface-200 rounded w-20"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    generateTableSkeleton(count) {
        return `
            <div class="animate-pulse">
                <div class="bg-white border border-surface-200 rounded-lg overflow-hidden">
                    <!-- Header -->
                    <div class="bg-surface-50 border-b border-surface-200 p-4 flex gap-4">
                        <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                        <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                        <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                        <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                    </div>
                    <!-- Rows -->
                    ${Array(count).fill().map(() => `
                        <div class="p-4 flex gap-4 border-b border-surface-100">
                            <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                            <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                            <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                            <div class="h-4 bg-surface-200 rounded w-1/4"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateFormSkeleton() {
        return `
            <div class="space-y-6 animate-pulse">
                ${Array(5).fill().map(() => `
                    <div class="space-y-2">
                        <div class="h-4 bg-surface-200 rounded w-32"></div>
                        <div class="h-10 bg-surface-200 rounded"></div>
                    </div>
                `).join('')}
                <div class="flex gap-3 justify-end pt-4">
                    <div class="h-10 bg-surface-200 rounded w-24"></div>
                    <div class="h-10 bg-surface-200 rounded w-32"></div>
                </div>
            </div>
        `;
    }

    hideSkeleton(container) {
        container.classList.remove('loading-skeleton');
    }

    /**
     * 2. EMPTY STATES
     * Show helpful empty states with CTAs
     */
    showEmptyState(container, config) {
        const {
            icon = '📭',
            title = 'No items yet',
            description = 'Get started by adding your first item',
            actionLabel = 'Add Item',
            actionHandler,
            secondaryAction = null,
            illustration = null
        } = config;

        const illustrationHTML = illustration ? 
            `<img src="${illustration}" alt="${title}" class="w-48 h-48 mx-auto mb-6 opacity-50">` :
            `<div class="text-7xl mb-6 opacity-50">${icon}</div>`;

        const secondaryActionHTML = secondaryAction ? `
            <button class="btn btn-text" onclick="${secondaryAction.handler}">
                ${secondaryAction.label}
            </button>
        ` : '';

        container.innerHTML = `
            <div class="empty-state text-center py-20 px-4 fade-in">
                ${illustrationHTML}
                <h3 class="text-2xl font-semibold text-surface-900 mb-3">${title}</h3>
                <p class="text-surface-600 mb-8 max-w-md mx-auto text-lg">${description}</p>
                <div class="flex gap-3 justify-center">
                    <button class="btn btn-primary btn-lg" onclick="${actionHandler}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        ${actionLabel}
                    </button>
                    ${secondaryActionHTML}
                </div>
            </div>
        `;
    }

    /**
     * 3. SEARCH PROGRESS INDICATOR
     * Show visual feedback during search
     */
    setupSearchProgress(inputElement, searchHandler) {
        inputElement.addEventListener('input', (e) => {
            const term = e.target.value;
            
            // Clear existing timeout
            if (this.searchTimeouts.has(inputElement)) {
                clearTimeout(this.searchTimeouts.get(inputElement));
            }

            if (term.length === 0) {
                inputElement.classList.remove('searching');
                searchHandler('');
                return;
            }

            // Show searching state
            inputElement.classList.add('searching');

            // Debounced search
            const timeout = setTimeout(async () => {
                try {
                    await searchHandler(term);
                } finally {
                    inputElement.classList.remove('searching');
                }
            }, 300);

            this.searchTimeouts.set(inputElement, timeout);
        });
    }

    /**
     * 4. KEYBOARD SHORTCUTS
     * Global keyboard shortcuts for common actions
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input/textarea
            if (e.target.matches('input, textarea, [contenteditable]')) {
                // Allow Escape to blur
                if (e.key === 'Escape') {
                    e.target.blur();
                }
                return;
            }

            const isMod = e.ctrlKey || e.metaKey;

            if (isMod) {
                switch(e.key.toLowerCase()) {
                    case 'n':
                        e.preventDefault();
                        this.triggerNewItem();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.focusSearch();
                        break;
                    case 's':
                        e.preventDefault();
                        this.saveCurrentForm();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.focusSearch();
                        break;
                }
            }

            // Standalone keys
            switch(e.key) {
                case 'Escape':
                    this.closeModals();
                    break;
                case '?':
                    if (!e.target.matches('input, textarea')) {
                        e.preventDefault();
                        this.showKeyboardShortcuts();
                    }
                    break;
            }
        });
    }

    triggerNewItem() {
        // Trigger new item based on current section
        const section = window.app?.currentSection;
        const actions = {
            'contacts': 'app.contacts.showContactForm()',
            'companies': 'app.companies.showCompanyForm()',
            'leads': 'app.leads.showLeadForm()',
            'deals': 'app.deals.showDealForm()',
            'tasks': 'app.tasks.showTaskForm()',
            'projects': 'app.projects.showProjectForm()',
            'memos': 'app.memos.showMemoForm()'
        };

        const action = actions[section];
        if (action) {
            eval(action);
        }
    }

    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"], input[placeholder*="search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    saveCurrentForm() {
        const activeForm = document.querySelector('form:not([hidden])');
        if (activeForm) {
            const submitButton = activeForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }

    closeModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => modal.remove());
    }

    showKeyboardShortcuts() {
        const shortcuts = [
            { key: '⌘/Ctrl + N', description: 'Create new item' },
            { key: '⌘/Ctrl + K', description: 'Focus search' },
            { key: '⌘/Ctrl + S', description: 'Save current form' },
            { key: 'Esc', description: 'Close modal or blur input' },
            { key: '?', description: 'Show this help' }
        ];

        const modalHTML = `
            <div class="modal-overlay fade-in">
                <div class="modal w-full max-w-md scale-in">
                    <div class="modal-header">
                        <h3 class="modal-title">Keyboard Shortcuts</h3>
                        <button class="btn-icon btn-text" onclick="this.closest('.modal-overlay').remove()">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="space-y-3">
                            ${shortcuts.map(s => `
                                <div class="flex items-center justify-between py-2">
                                    <span class="text-surface-700">${s.description}</span>
                                    <kbd class="px-3 py-1 text-sm bg-surface-100 border border-surface-300 rounded">${s.key}</kbd>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    /**
     * Show backend validation errors on a form
     */
    /**
     * Show backend validation errors inline on a form
     * @param {HTMLFormElement} form - The form element
     * @param {any} error - Error object/response from API layer
     */
    showFormErrors(form, error) {
        // Try to parse error response
        let data = null;
        try {
            if (error && error.responseJSON) {
                data = error.responseJSON;
            } else if (error && error.response && typeof error.response.json === 'function') {
                data = error.response.json();
            } else if (error && error.message) {
                // leave message for generic toast
            }
        } catch (e) {
            // ignore
        }

        if (!data || typeof data !== 'object') {
            // Show generic error
            window.app?.showToast('Validation failed. Please check inputs.', 'error');
            return;
        }

        // Clear previous messages
        form.querySelectorAll('.validation-message').forEach(el => el.remove());
        form.querySelectorAll('.input').forEach(el => el.classList.remove('border-error-500'));

        Object.entries(data).forEach(([field, messages]) => {
            const input = form.querySelector(`[name="${field}"]`);
            const messageText = Array.isArray(messages) ? messages.join(' ') : String(messages);
            if (input) {
                // Mark input and append message
                input.classList.add('border-error-500');
                const parent = input.closest('.input-group') || input.parentElement;
                const msg = document.createElement('p');
                msg.className = 'validation-message text-error-600 text-sm mt-1';
                msg.textContent = messageText;
                parent.appendChild(msg);
            }
        });
    }

    /**
     * Trap focus inside a modal overlay (a11y)
     * @param {HTMLElement} overlayEl
     */
    applyFocusTrap(overlayEl) {
        if (!overlayEl) return;
        const dialog = overlayEl.querySelector('.modal') || overlayEl.firstElementChild;
        if (!dialog) return;
        dialog.setAttribute('role', 'dialog');
        overlayEl.setAttribute('aria-modal', 'true');
        const getFocusable = () => Array.from(dialog.querySelectorAll('a, button, textarea, input, select, [tabindex]:not([tabindex="-1"])')).filter(el => !el.hasAttribute('disabled'));
        const focusables = getFocusable();
        if (focusables.length) {
            // Focus the first focusable
            focusables[0].focus();
        } else {
            dialog.setAttribute('tabindex', '-1');
            dialog.focus();
        }
        const onKeyDown = (e) => {
            if (e.key !== 'Tab') return;
            const f = getFocusable();
            if (f.length === 0) return;
            const first = f[0];
            const last = f[f.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        };
        overlayEl.addEventListener('keydown', onKeyDown);
    }

    /**
     * 5. SMART DEFAULTS
     * Auto-fill forms with intelligent defaults
     */
    getSmartDefaults(formType, userId) {
        const defaults = {
            owner: userId
        };

        // Get last used values
        const lastCountry = this.lastUsedValues.get('country');
        const lastLeadSource = this.lastUsedValues.get('lead_source');
        const lastIndustry = this.lastUsedValues.get('industry');

        if (lastCountry) defaults.country = lastCountry;
        if (lastLeadSource) defaults.lead_source = lastLeadSource;
        if (lastIndustry) defaults.industry = lastIndustry;

        // Auto-detect timezone
        defaults.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Try to get email from clipboard
        this.detectEmailInClipboard().then(email => {
            if (email) {
                const emailInput = document.querySelector('input[type="email"]');
                if (emailInput && !emailInput.value) {
                    emailInput.value = email;
                }
            }
        });

        return defaults;
    }

    async detectEmailInClipboard() {
        try {
            const text = await navigator.clipboard.readText();
            const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
            const match = text.match(emailRegex);
            return match ? match[0] : null;
        } catch {
            return null;
        }
    }

    rememberValue(field, value) {
        if (value) {
            this.lastUsedValues.set(field, value);
            localStorage.setItem(`last_${field}`, value);
        }
    }

    loadLastUsedValues() {
        ['country', 'lead_source', 'industry'].forEach(field => {
            const value = localStorage.getItem(`last_${field}`);
            if (value) {
                this.lastUsedValues.set(field, value);
            }
        });
    }

    applySmartDefaults(form, defaults) {
        Object.entries(defaults).forEach(([field, value]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input && !input.value) {
                input.value = value;
            }
        });
    }

    /**
     * 6. ERROR RECOVERY FLOW
     * Show actionable error messages with recovery options
     */
    showErrorModal(config) {
        const {
            title = 'An error occurred',
            message = 'Something went wrong. Please try again.',
            error = null,
            actions = [
                { label: 'Try Again', handler: null, primary: true },
                { label: 'Cancel', handler: null, primary: false }
            ],
            technical = null
        } = config;

        const technicalDetails = technical || (error?.message ? `
            <details class="mt-4">
                <summary class="text-sm text-surface-600 cursor-pointer hover:text-surface-900">
                    Technical details
                </summary>
                <pre class="mt-2 p-3 bg-surface-50 rounded text-xs overflow-auto">${error.message}</pre>
            </details>
        ` : '');

        const actionsHTML = actions.map(action => {
            const btnClass = action.primary ? 'btn-primary' : 'btn-secondary';
            return `
                <button class="btn ${btnClass}" onclick="${action.handler}; this.closest('.modal-overlay').remove()">
                    ${action.label}
                </button>
            `;
        }).join('');

        const modalHTML = `
            <div class="modal-overlay fade-in">
                <div class="modal w-full max-w-md scale-in">
                    <div class="modal-header bg-error-50">
                        <div class="flex items-center gap-3">
                            <svg class="w-6 h-6 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                            </svg>
                            <h3 class="modal-title">${title}</h3>
                        </div>
                    </div>
                    <div class="modal-body">
                        <p class="text-surface-700 leading-relaxed">${message}</p>
                        ${technicalDetails}
                    </div>
                    <div class="modal-footer">
                        ${actionsHTML}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    /**
     * 7. OPTIMISTIC UI UPDATES
     * Update UI immediately, rollback on error
     */
    optimisticUpdate(config) {
        const {
            item,
            action, // 'create', 'update', 'delete'
            apiCall,
            onSuccess,
            onError,
            listElement
        } = config;

        // Generate temporary ID
        const tempId = `temp_${Date.now()}`;
        item.id = item.id || tempId;
        item._isOptimistic = true;

        // Apply UI update immediately
        switch(action) {
            case 'create':
                this.addItemToList(item, listElement);
                break;
            case 'update':
                this.updateItemInList(item, listElement);
                break;
            case 'delete':
                this.removeItemFromList(item.id, listElement);
                break;
        }

        // Make API call
        apiCall()
            .then(result => {
                // Update with real data
                if (action === 'create') {
                    this.replaceOptimisticItem(tempId, result, listElement);
                }
                if (onSuccess) onSuccess(result);
            })
            .catch(error => {
                // Rollback on error
                switch(action) {
                    case 'create':
                        this.removeItemFromList(tempId, listElement);
                        break;
                    case 'update':
                        // Would need original item to restore
                        break;
                    case 'delete':
                        this.addItemToList(item, listElement);
                        break;
                }
                
                if (onError) onError(error);
                
                this.showErrorModal({
                    title: `Failed to ${action} item`,
                    message: error.message || 'Please try again',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: `uxEnhancements.optimisticUpdate(${JSON.stringify(config)})`, primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            });
    }

    addItemToList(item, listElement) {
        // Implementation depends on list structure
        // This is a generic placeholder
        const itemHTML = this.renderListItem(item);
        listElement.insertAdjacentHTML('afterbegin', itemHTML);
    }

    updateItemInList(item, listElement) {
        const existingItem = listElement.querySelector(`[data-id="${item.id}"]`);
        if (existingItem) {
            const newHTML = this.renderListItem(item);
            existingItem.outerHTML = newHTML;
        }
    }

    removeItemFromList(itemId, listElement) {
        const item = listElement.querySelector(`[data-id="${itemId}"]`);
        if (item) {
            item.classList.add('fade-out');
            setTimeout(() => item.remove(), 300);
        }
    }

    replaceOptimisticItem(tempId, realItem, listElement) {
        const tempElement = listElement.querySelector(`[data-id="${tempId}"]`);
        if (tempElement) {
            tempElement.setAttribute('data-id', realItem.id);
            delete realItem._isOptimistic;
            // Update any data attributes or content that changed
        }
    }

    renderListItem(item) {
        // This should be implemented by each module
        // Return HTML string for the item
        return `<div data-id="${item.id}">${item.name || 'Item'}</div>`;
    }
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.uxEnhancements = new UXEnhancements();
    window.uxEnhancements.loadLastUsedValues();
}
