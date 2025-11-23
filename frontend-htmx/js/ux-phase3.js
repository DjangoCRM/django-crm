/**
 * UX Enhancements Phase 3
 * Infinite Scroll, Inline Editing, Drag & Drop, Context Menu, Duplicate Detection
 */

class Phase3UXEnhancements {
    constructor() {
        this.observers = new Map();
        this.editingCell = null;
        this.contextMenus = new Map();
    }

    /**
     * INFINITE SCROLL PAGINATION
     * Load more items as user scrolls
     */
    setupInfiniteScroll(config) {
        const {
            container,
            loadMoreFunction,
            threshold = 0.8, // Trigger when 80% scrolled
            hasMore = () => true
        } = config;

        const sentinel = document.createElement('div');
        sentinel.className = 'infinite-scroll-sentinel';
        sentinel.style.height = '1px';
        container.appendChild(sentinel);

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && hasMore() && !this.isLoading) {
                    this.loadMore(loadMoreFunction);
                }
            });
        }, {
            root: null,
            rootMargin: '0px',
            threshold: threshold
        });

        observer.observe(sentinel);
        this.observers.set(container, { observer, sentinel });

        return () => {
            observer.disconnect();
            sentinel.remove();
            this.observers.delete(container);
        };
    }

    async loadMore(loadMoreFunction) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingIndicator();

        try {
            await loadMoreFunction();
        } catch (error) {
            console.error('Error loading more items:', error);
            if (window.app) {
                window.app.showToast('Failed to load more items', 'error');
            }
        } finally {
            this.isLoading = false;
            this.hideLoadingIndicator();
        }
    }

    showLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'infinite-scroll-loader';
        indicator.className = 'flex justify-center items-center py-8';
        indicator.innerHTML = `
            <div class="spinner"></div>
            <span class="ml-3 text-surface-600">Loading more...</span>
        `;
        
        const sentinels = document.querySelectorAll('.infinite-scroll-sentinel');
        sentinels.forEach(sentinel => {
            if (sentinel.parentNode) {
                sentinel.parentNode.insertBefore(indicator, sentinel);
            }
        });
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('infinite-scroll-loader');
        if (indicator) {
            indicator.remove();
        }
    }

    disconnectInfiniteScroll(container) {
        const data = this.observers.get(container);
        if (data) {
            data.observer.disconnect();
            data.sentinel.remove();
            this.observers.delete(container);
        }
    }

    /**
     * INLINE EDITING
     * Edit table cells directly
     */
    enableInlineEditing(config) {
        const {
            table,
            editableSelector = '.editable',
            onSave,
            allowedTypes = ['text', 'number', 'select', 'date']
        } = config;

        table.addEventListener('dblclick', (e) => {
            const cell = e.target.closest(editableSelector);
            if (!cell || this.editingCell) return;

            this.startInlineEdit(cell, onSave);
        });

        // Also allow click on edit icon
        table.addEventListener('click', (e) => {
            if (e.target.closest('.inline-edit-trigger')) {
                const cell = e.target.closest('td, th').querySelector(editableSelector);
                if (cell && !this.editingCell) {
                    this.startInlineEdit(cell, onSave);
                }
            }
        });
    }

    startInlineEdit(cell, onSave) {
        this.editingCell = cell;
        const originalValue = cell.textContent.trim();
        const fieldType = cell.dataset.type || 'text';
        const fieldName = cell.dataset.field;
        const itemId = cell.closest('tr').dataset.id;

        cell.classList.add('editing');
        
        let inputHTML;
        switch (fieldType) {
            case 'select':
                const options = JSON.parse(cell.dataset.options || '[]');
                inputHTML = `
                    <select class="inline-edit-input">
                        ${options.map(opt => `
                            <option value="${opt.value}" ${opt.value === originalValue ? 'selected' : ''}>
                                ${opt.label}
                            </option>
                        `).join('')}
                    </select>
                `;
                break;
            case 'date':
                inputHTML = `<input type="date" class="inline-edit-input" value="${originalValue}">`;
                break;
            case 'number':
                inputHTML = `<input type="number" class="inline-edit-input" value="${originalValue}">`;
                break;
            default:
                inputHTML = `<input type="text" class="inline-edit-input" value="${originalValue}">`;
        }

        cell.innerHTML = inputHTML;
        const input = cell.querySelector('.inline-edit-input');
        input.focus();
        if (input.select) input.select();

        // Save on blur or Enter
        const save = async () => {
            const newValue = input.value;
            
            if (newValue === originalValue) {
                this.cancelInlineEdit(cell, originalValue);
                return;
            }

            // Show loading
            cell.innerHTML = '<div class="spinner"></div>';

            try {
                await onSave(itemId, fieldName, newValue);
                cell.textContent = newValue;
                cell.classList.remove('editing');
                this.editingCell = null;
                
                // Success animation
                cell.classList.add('flash-success');
                setTimeout(() => cell.classList.remove('flash-success'), 1000);
                
            } catch (error) {
                // Revert on error
                cell.textContent = originalValue;
                cell.classList.remove('editing');
                this.editingCell = null;
                
                if (window.app) {
                    window.app.showToast('Failed to save changes', 'error');
                }
            }
        };

        const cancel = () => {
            this.cancelInlineEdit(cell, originalValue);
        };

        input.addEventListener('blur', save);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                save();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancel();
            }
        });
    }

    cancelInlineEdit(cell, originalValue) {
        cell.textContent = originalValue;
        cell.classList.remove('editing');
        this.editingCell = null;
    }

    /**
     * DRAG & DROP FILE UPLOAD
     * Upload files by dragging into drop zone
     */
    setupDragAndDrop(config) {
        const {
            dropZone,
            onFiles,
            acceptedTypes = ['*'],
            maxSize = 10 * 1024 * 1024, // 10MB
            multiple = true
        } = config;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop zone when dragging
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });

        // Handle drop
        dropZone.addEventListener('drop', async (e) => {
            const files = Array.from(e.dataTransfer.files);
            
            // Validate files
            const validFiles = files.filter(file => {
                // Check type
                if (acceptedTypes[0] !== '*') {
                    const fileType = file.type || '';
                    const fileExt = '.' + file.name.split('.').pop();
                    const isAccepted = acceptedTypes.some(type => 
                        fileType.match(type.replace('*', '.*')) || fileExt === type
                    );
                    if (!isAccepted) return false;
                }
                
                // Check size
                if (file.size > maxSize) {
                    if (window.app) {
                        window.app.showToast(`File ${file.name} is too large (max ${maxSize / 1024 / 1024}MB)`, 'error');
                    }
                    return false;
                }
                
                return true;
            });

            if (validFiles.length > 0) {
                if (!multiple && validFiles.length > 1) {
                    validFiles.splice(1);
                }
                
                await onFiles(validFiles);
            }
        });

        // Also handle click to select files
        dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = multiple;
            if (acceptedTypes[0] !== '*') {
                input.accept = acceptedTypes.join(',');
            }
            
            input.addEventListener('change', async () => {
                const files = Array.from(input.files);
                if (files.length > 0) {
                    await onFiles(files);
                }
            });
            
            input.click();
        });
    }

    /**
     * CONTEXT MENU (Right-click menu)
     * Show custom menu on right-click
     */
    setupContextMenu(config) {
        const {
            target,
            menuItems,
            onItemClick
        } = config;

        target.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            
            const itemId = e.target.closest('[data-id]')?.dataset.id;
            if (!itemId) return;

            this.showContextMenu(e.clientX, e.clientY, menuItems, (action) => {
                onItemClick(itemId, action);
            });
        });
    }

    showContextMenu(x, y, items, onSelect) {
        // Remove existing menus
        this.hideContextMenu();

        const menu = document.createElement('div');
        menu.className = 'context-menu fade-in';
        menu.style.left = `${x}px`;
        menu.style.top = `${y}px`;
        
        menu.innerHTML = items.map(item => {
            if (item === 'divider') {
                return '<div class="context-menu-divider"></div>';
            }
            
            return `
                <div class="context-menu-item" data-action="${item.action}">
                    ${item.icon ? `<span class="text-lg">${item.icon}</span>` : ''}
                    <span>${item.label}</span>
                    ${item.shortcut ? `<kbd class="ml-auto">${item.shortcut}</kbd>` : ''}
                </div>
            `;
        }).join('');

        document.body.appendChild(menu);

        // Position adjustment if off-screen
        const rect = menu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            menu.style.left = `${x - rect.width}px`;
        }
        if (rect.bottom > window.innerHeight) {
            menu.style.top = `${y - rect.height}px`;
        }

        // Handle clicks
        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (item) {
                const action = item.dataset.action;
                onSelect(action);
                this.hideContextMenu();
            }
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', () => this.hideContextMenu(), { once: true });
        }, 0);

        this.contextMenus.set(menu, true);
    }

    hideContextMenu() {
        this.contextMenus.forEach((_, menu) => {
            menu.remove();
        });
        this.contextMenus.clear();
    }

    /**
     * DUPLICATE DETECTION
     * Check for potential duplicates when creating/editing
     */
    async checkDuplicates(config) {
        const {
            fields,
            checkFunction,
            onDuplicatesFound
        } = config;

        try {
            const duplicates = await checkFunction(fields);
            
            if (duplicates && duplicates.length > 0) {
                this.showDuplicateWarning(duplicates, onDuplicatesFound);
                return duplicates;
            }
            
            return null;
        } catch (error) {
            console.error('Error checking duplicates:', error);
            return null;
        }
    }

    showDuplicateWarning(duplicates, onDuplicatesFound) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay fade-in';
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header bg-warning-50">
                    <div class="flex items-center gap-3">
                        <svg class="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        </svg>
                        <h3 class="modal-title">Possible Duplicates Found</h3>
                    </div>
                </div>
                <div class="modal-body">
                    <p class="text-surface-700 mb-4">
                        We found ${duplicates.length} similar ${duplicates.length === 1 ? 'record' : 'records'}. 
                        Please review before continuing:
                    </p>
                    
                    <div class="space-y-3 max-h-96 overflow-y-auto">
                        ${duplicates.map(dup => `
                            <div class="duplicate-warning p-4 flex items-start gap-4 cursor-pointer hover:bg-warning-100 transition-colors rounded-lg"
                                 onclick="phase3UX.viewDuplicate('${dup.id}')">
                                <div class="avatar avatar-md bg-warning-100">
                                    <span class="text-warning-600">${(dup.name || '?').charAt(0).toUpperCase()}</span>
                                </div>
                                <div class="flex-1">
                                    <h4 class="font-semibold text-surface-900">${dup.name || 'Unknown'}</h4>
                                    ${dup.email ? `<p class="text-sm text-surface-600">${dup.email}</p>` : ''}
                                    ${dup.phone ? `<p class="text-sm text-surface-600">${dup.phone}</p>` : ''}
                                    <p class="text-xs text-surface-500 mt-1">
                                        Similarity: ${Math.round(dup.similarity * 100)}%
                                    </p>
                                </div>
                                <button class="btn btn-text btn-sm" onclick="event.stopPropagation(); phase3UX.viewDuplicate('${dup.id}')">
                                    View
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                        Cancel
                    </button>
                    <button class="btn btn-text" onclick="phase3UX.handleDuplicateAction('view')">
                        Review Similar
                    </button>
                    <button class="btn btn-primary" onclick="phase3UX.handleDuplicateAction('continue'); this.closest('.modal-overlay').remove()">
                        Create Anyway
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        this.currentDuplicates = duplicates;
        this.onDuplicatesCallback = onDuplicatesFound;
    }

    viewDuplicate(id) {
        console.log('View duplicate:', id);
        // Implementation depends on module
        if (this.onDuplicatesCallback) {
            this.onDuplicatesCallback('view', id);
        }
    }

    handleDuplicateAction(action) {
        if (this.onDuplicatesCallback) {
            this.onDuplicatesCallback(action, this.currentDuplicates);
        }
    }

    /**
     * ADVANCED FILTERING UI
     * Build complex filters visually
     */
    setupAdvancedFilters(config) {
        const {
            container,
            fields,
            onFilterChange
        } = config;

        const filterBuilder = document.createElement('div');
        filterBuilder.className = 'advanced-filters card p-6 mb-6';
        filterBuilder.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold">Filters</h3>
                <div class="flex gap-2">
                    <button class="btn btn-text btn-sm" onclick="phase3UX.clearFilters()">Clear All</button>
                    <button class="btn btn-primary btn-sm" onclick="phase3UX.addFilterRow()">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Add Filter
                    </button>
                </div>
            </div>
            <div id="filter-rows" class="space-y-3"></div>
        `;

        container.insertBefore(filterBuilder, container.firstChild);

        this.filterConfig = { fields, onFilterChange, container: filterBuilder };
        this.filters = [];
    }

    addFilterRow() {
        const filterId = Date.now();
        const row = document.createElement('div');
        row.className = 'filter-row flex gap-3 items-start';
        row.dataset.filterId = filterId;
        
        const fields = this.filterConfig.fields;
        
        row.innerHTML = `
            <select class="input select flex-1" onchange="phase3UX.updateFilterOperators(${filterId})">
                <option value="">Select field...</option>
                ${fields.map(f => `<option value="${f.name}">${f.label}</option>`).join('')}
            </select>
            <select class="input select w-32" data-operators>
                <option value="equals">Equals</option>
                <option value="contains">Contains</option>
                <option value="starts_with">Starts with</option>
                <option value="ends_with">Ends with</option>
                <option value="greater_than">Greater than</option>
                <option value="less_than">Less than</option>
            </select>
            <input type="text" class="input flex-1" placeholder="Value..." data-value>
            <button class="btn-icon btn-text" onclick="phase3UX.removeFilterRow(${filterId})">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
            </button>
        `;

        document.getElementById('filter-rows').appendChild(row);
        this.filters.push({ id: filterId, field: '', operator: 'equals', value: '' });
    }

    removeFilterRow(filterId) {
        const row = document.querySelector(`[data-filter-id="${filterId}"]`);
        if (row) {
            row.remove();
            this.filters = this.filters.filter(f => f.id !== filterId);
            this.applyFilters();
        }
    }

    updateFilterOperators(filterId) {
        // Implementation for field-specific operators
    }

    clearFilters() {
        document.getElementById('filter-rows').innerHTML = '';
        this.filters = [];
        this.applyFilters();
    }

    applyFilters() {
        if (this.filterConfig.onFilterChange) {
            this.filterConfig.onFilterChange(this.filters);
        }
    }
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.phase3UX = new Phase3UXEnhancements();
}
