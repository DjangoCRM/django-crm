/**
 * Advanced UX Enhancements Module
 * Phase 2: Optimistic UI, Bulk Actions, Real-time Validation, etc.
 */

class AdvancedUXEnhancements {
    constructor() {
        this.pendingOperations = new Map();
        this.selectedItems = new Set();
        this.bulkActionBar = null;
        this.validationTimeouts = new Map();
    }

    /**
     * OPTIMISTIC UI UPDATES
     * Update UI immediately, rollback on error
     */
    async optimisticCreate(config) {
        const {
            item,
            container,
            apiCall,
            renderFunction,
            onSuccess,
            onError
        } = config;

        // Generate temporary ID
        const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        item.id = tempId;
        item._optimistic = true;

        // Add to UI immediately
        const itemHTML = renderFunction(item);
        const tempElement = document.createElement('div');
        tempElement.innerHTML = itemHTML;
        const itemElement = tempElement.firstElementChild;
        itemElement.setAttribute('data-optimistic', 'true');
        
        if (container.firstElementChild) {
            container.insertBefore(itemElement, container.firstElementChild);
        } else {
            container.appendChild(itemElement);
        }

        // Animate in
        itemElement.classList.add('scale-in');

        // Store operation
        this.pendingOperations.set(tempId, { item, itemElement });

        try {
            // Make API call
            const result = await apiCall();
            
            // Update with real data
            itemElement.setAttribute('data-id', result.id);
            itemElement.removeAttribute('data-optimistic');
            delete item._optimistic;
            
            // Update any content that changed
            const updatedHTML = renderFunction(result);
            const updatedElement = document.createElement('div');
            updatedElement.innerHTML = updatedHTML;
            itemElement.innerHTML = updatedElement.firstElementChild.innerHTML;
            
            this.pendingOperations.delete(tempId);
            
            if (onSuccess) onSuccess(result);
            
        } catch (error) {
            // Rollback: remove from UI
            itemElement.classList.add('fade-out');
            setTimeout(() => itemElement.remove(), 300);
            
            this.pendingOperations.delete(tempId);
            
            if (onError) onError(error);
            
            // Show error
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: 'Failed to create item',
                    message: error.message || 'Please try again',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: () => this.optimisticCreate(config), primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            }
        }
    }

    async optimisticUpdate(config) {
        const {
            itemId,
            updates,
            element,
            apiCall,
            renderFunction,
            onSuccess,
            onError
        } = config;

        // Save original state
        const originalHTML = element.innerHTML;
        const originalData = { ...element.dataset };

        // Apply updates to UI
        element.setAttribute('data-optimistic', 'true');
        if (renderFunction) {
            const updatedHTML = renderFunction({ id: itemId, ...updates });
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = updatedHTML;
            element.innerHTML = tempDiv.firstElementChild.innerHTML;
        }

        try {
            // Make API call
            const result = await apiCall();
            
            // Update with real data
            element.removeAttribute('data-optimistic');
            if (renderFunction) {
                const finalHTML = renderFunction(result);
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = finalHTML;
                element.innerHTML = tempDiv.firstElementChild.innerHTML;
            }
            
            if (onSuccess) onSuccess(result);
            
        } catch (error) {
            // Rollback: restore original
            element.innerHTML = originalHTML;
            Object.keys(originalData).forEach(key => {
                element.dataset[key] = originalData[key];
            });
            element.removeAttribute('data-optimistic');
            
            if (onError) onError(error);
            
            // Show error
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: 'Failed to update item',
                    message: error.message || 'Changes were not saved',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: () => this.optimisticUpdate(config), primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            }
        }
    }

    async optimisticDelete(config) {
        const {
            itemId,
            element,
            apiCall,
            onSuccess,
            onError,
            undoData
        } = config;

        // Animate out
        element.classList.add('fade-out');
        
        // Store for potential undo
        const originalParent = element.parentNode;
        const originalNextSibling = element.nextSibling;
        
        setTimeout(() => {
            element.style.display = 'none';
        }, 300);

        try {
            // Make API call
            await apiCall();
            
            // Remove from DOM
            element.remove();
            
            if (onSuccess) onSuccess();
            
            // Show undo toast
            this.showUndoToast('Item deleted', undoData, () => {
                // Undo: restore element
                element.classList.remove('fade-out');
                element.style.display = '';
                if (originalNextSibling) {
                    originalParent.insertBefore(element, originalNextSibling);
                } else {
                    originalParent.appendChild(element);
                }
                element.classList.add('scale-in');
            });
            
        } catch (error) {
            // Rollback: restore element
            element.classList.remove('fade-out');
            element.style.display = '';
            
            if (onError) onError(error);
            
            // Show error
            if (window.uxEnhancements) {
                window.uxEnhancements.showErrorModal({
                    title: 'Failed to delete item',
                    message: error.message || 'Please try again',
                    error: error,
                    actions: [
                        { label: 'Try Again', handler: () => this.optimisticDelete(config), primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            }
        }
    }

    showUndoToast(message, undoData, undoHandler) {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = 'toast toast-success toast-with-action fade-in pointer-events-auto';
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span>${message}</span>
            </div>
            <button class="toast-action-button" id="undo-btn-${Date.now()}">
                Undo
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Undo handler
        const undoBtn = toast.querySelector('.toast-action-button');
        undoBtn.addEventListener('click', () => {
            undoHandler();
            toast.remove();
            if (window.app) {
                window.app.showToast('Action undone', 'success');
            }
        });
        
        // Auto-remove after 8 seconds
        setTimeout(() => toast.remove(), 8000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-3 pointer-events-none';
        document.body.appendChild(container);
        return container;
    }

    /**
     * BULK ACTIONS
     * Select multiple items and perform actions
     */
    enableBulkSelection(containerSelector, itemSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        // Add checkboxes to items
        container.addEventListener('click', (e) => {
            if (e.target.matches('.bulk-checkbox, .bulk-checkbox *')) {
                const checkbox = e.target.closest('.bulk-checkbox').querySelector('input[type="checkbox"]');
                const itemId = checkbox.value;
                
                if (checkbox.checked) {
                    this.selectedItems.add(itemId);
                } else {
                    this.selectedItems.delete(itemId);
                }
                
                this.updateBulkActionBar();
            }
        });

        // Select all checkbox
        const selectAllCheckbox = container.querySelector('#select-all-checkbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = container.querySelectorAll('.bulk-checkbox input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    cb.checked = e.target.checked;
                    if (e.target.checked) {
                        this.selectedItems.add(cb.value);
                    } else {
                        this.selectedItems.delete(cb.value);
                    }
                });
                this.updateBulkActionBar();
            });
        }
    }

    updateBulkActionBar() {
        if (this.selectedItems.size === 0) {
            if (this.bulkActionBar) {
                this.bulkActionBar.remove();
                this.bulkActionBar = null;
            }
            return;
        }

        if (!this.bulkActionBar) {
            this.bulkActionBar = this.createBulkActionBar();
            document.body.appendChild(this.bulkActionBar);
        }

        // Update count
        const countElement = this.bulkActionBar.querySelector('.selection-count');
        if (countElement) {
            countElement.textContent = `${this.selectedItems.size} selected`;
        }
    }

    createBulkActionBar() {
        const bar = document.createElement('div');
        bar.className = 'bulk-action-bar';
        bar.innerHTML = `
            <span class="selection-count font-medium text-surface-900"></span>
            <div class="flex gap-2">
                <button class="btn btn-sm btn-secondary" onclick="advancedUX.bulkEdit()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Edit
                </button>
                <button class="btn btn-sm btn-secondary" onclick="advancedUX.bulkExport()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                    Export
                </button>
                <button class="btn btn-sm btn-secondary text-error-600" onclick="advancedUX.bulkDelete()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    Delete
                </button>
            </div>
            <button class="btn-icon btn-text" onclick="advancedUX.clearSelection()">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        return bar;
    }

    clearSelection() {
        this.selectedItems.clear();
        document.querySelectorAll('.bulk-checkbox input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        this.updateBulkActionBar();
    }

    bulkEdit() {
        console.log('Bulk edit:', Array.from(this.selectedItems));
        // Implementation depends on module
        if (window.app && window.app.currentSection) {
            const section = window.app.currentSection;
            // Show bulk edit modal
            this.showBulkEditModal(section, Array.from(this.selectedItems));
        }
    }

    bulkExport() {
        console.log('Bulk export:', Array.from(this.selectedItems));
        // Export selected items
        const ids = Array.from(this.selectedItems);
        if (window.app) {
            window.app.showToast(`Exporting ${ids.length} items...`, 'info');
            // Implementation depends on module
        }
    }

    async bulkDelete() {
        const ids = Array.from(this.selectedItems);
        
        if (!confirm(`Delete ${ids.length} items? This cannot be undone.`)) {
            return;
        }

        console.log('Bulk delete:', ids);
        
        // Show progress
        if (window.app) {
            window.app.showToast(`Deleting ${ids.length} items...`, 'info');
        }

        // Implementation depends on module
        this.clearSelection();
    }

    showBulkEditModal(section, ids) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay fade-in';
        modal.innerHTML = `
            <div class="modal w-full max-w-lg scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">Bulk Edit ${ids.length} Items</h3>
                    <button class="btn-icon btn-text" onclick="this.closest('.modal-overlay').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <form id="bulk-edit-form" class="modal-body space-y-4">
                    <p class="text-surface-600">Select fields to update for all ${ids.length} selected items:</p>
                    
                    <div class="space-y-4">
                        <label class="flex items-center gap-3">
                            <input type="checkbox" class="checkbox" name="update_status" value="1">
                            <span>Update Status</span>
                        </label>
                        <div class="ml-8 input-group">
                            <select class="input" name="status" disabled>
                                <option>Active</option>
                                <option>Inactive</option>
                                <option>Pending</option>
                            </select>
                        </div>

                        <label class="flex items-center gap-3">
                            <input type="checkbox" class="checkbox" name="update_owner" value="1">
                            <span>Update Owner</span>
                        </label>
                        <div class="ml-8 input-group">
                            <select class="input" name="owner" disabled>
                                <option>Select owner...</option>
                            </select>
                        </div>

                        <label class="flex items-center gap-3">
                            <input type="checkbox" class="checkbox" name="update_tags" value="1">
                            <span>Add Tags</span>
                        </label>
                        <div class="ml-8 input-group">
                            <input type="text" class="input" name="tags" placeholder="tag1, tag2, tag3" disabled>
                        </div>
                    </div>
                </form>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="bulk-edit-form" class="btn btn-primary">
                        Update ${ids.length} Items
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Enable/disable inputs based on checkbox
        modal.querySelectorAll('input[type="checkbox"][name^="update_"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const fieldName = e.target.name.replace('update_', '');
                const input = modal.querySelector(`[name="${fieldName}"]`);
                if (input) {
                    input.disabled = !e.target.checked;
                }
            });
        });

        // Form submission
        modal.querySelector('#bulk-edit-form').addEventListener('submit', (e) => {
            e.preventDefault();
            // Collect updates
            const updates = {};
            const formData = new FormData(e.target);
            
            if (formData.get('update_status')) {
                updates.status = formData.get('status');
            }
            if (formData.get('update_owner')) {
                updates.owner = formData.get('owner');
            }
            if (formData.get('update_tags')) {
                updates.tags = formData.get('tags').split(',').map(t => t.trim());
            }

            console.log('Bulk updates:', updates, 'for ids:', ids);
            
            modal.remove();
            if (window.app) {
                window.app.showToast(`Updated ${ids.length} items`, 'success');
            }
        });
    }

    /**
     * REAL-TIME VALIDATION
     * Validate fields as user types
     */
    setupRealtimeValidation(form, rules) {
        Object.entries(rules).forEach(([fieldName, validators]) => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (!field) return;

            field.addEventListener('blur', async () => {
                await this.validateField(field, validators);
            });

            field.addEventListener('input', () => {
                // Clear previous timeout
                if (this.validationTimeouts.has(fieldName)) {
                    clearTimeout(this.validationTimeouts.get(fieldName));
                }

                // Debounced validation
                const timeout = setTimeout(async () => {
                    await this.validateField(field, validators);
                }, 500);

                this.validationTimeouts.set(fieldName, timeout);
            });
        });
    }

    async validateField(field, validators) {
        const value = field.value;
        
        // Clear previous validation
        this.clearFieldValidation(field);

        for (const validator of validators) {
            const result = await validator.check(value);
            
            if (!result.valid) {
                this.showFieldError(field, result.message, validator.type);
                return false;
            }
        }

        this.showFieldSuccess(field);
        return true;
    }

    clearFieldValidation(field) {
        field.classList.remove('border-error-500', 'border-success-500', 'border-warning-500');
        
        const parent = field.closest('.input-group') || field.parentElement;
        const existingMsg = parent.querySelector('.validation-message');
        if (existingMsg) {
            existingMsg.remove();
        }
    }

    showFieldError(field, message, type = 'error') {
        const colorClass = type === 'warning' ? 'border-warning-500' : 'border-error-500';
        const textColorClass = type === 'warning' ? 'text-warning-600' : 'text-error-600';
        
        field.classList.add(colorClass);
        
        const parent = field.closest('.input-group') || field.parentElement;
        const msg = document.createElement('p');
        msg.className = `validation-message ${textColorClass} text-sm mt-1`;
        msg.textContent = message;
        parent.appendChild(msg);
    }

    showFieldSuccess(field) {
        field.classList.add('border-success-500');
        
        const parent = field.closest('.input-group') || field.parentElement;
        const msg = document.createElement('p');
        msg.className = 'validation-message text-success-600 text-sm mt-1';
        msg.innerHTML = `
            <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Valid
        `;
        parent.appendChild(msg);
    }

    /**
     * PROGRESSIVE DISCLOSURE
     * Show/hide advanced fields
     */
    setupProgressiveDisclosure(form) {
        const advancedFields = form.querySelectorAll('[data-advanced="true"]');
        if (advancedFields.length === 0) return;

        // Hide advanced fields initially
        advancedFields.forEach(field => {
            const group = field.closest('.input-group') || field.parentElement;
            group.style.display = 'none';
        });

        // Add toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'btn btn-text mt-4';
        toggleBtn.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Show advanced fields
        `;

        // Insert before submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.parentElement.insertBefore(toggleBtn, submitBtn.parentElement.firstChild);
        } else {
            form.appendChild(toggleBtn);
        }

        // Toggle handler
        let expanded = false;
        toggleBtn.addEventListener('click', () => {
            expanded = !expanded;
            
            advancedFields.forEach(field => {
                const group = field.closest('.input-group') || field.parentElement;
                group.style.display = expanded ? '' : 'none';
                
                if (expanded) {
                    group.classList.add('slide-up');
                }
            });

            toggleBtn.innerHTML = expanded ? `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                </svg>
                Hide advanced fields
            ` : `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Show advanced fields
            `;
        });
    }
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.advancedUX = new AdvancedUXEnhancements();
}
