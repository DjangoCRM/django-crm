// Memo management functionality
class MemoManager {
    constructor(app) {
        this.app = app;
        this.currentMemos = [];
    }

    async loadMemos() {
        const section = document.getElementById('memos-section');
        if (!section) return;

        section.innerHTML = `
            <div class="bg-white rounded-lg shadow p-6 dark:bg-slate-800">
                <!-- Header -->
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Memos</h2>
                    <button onclick="app.memos.showMemoForm()" class="btn btn-primary">
                        <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        New Memo
                    </button>
                </div>

                <!-- Filters -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="input-group">
                        <input type="text" 
                               id="memo-search" 
                               placeholder="Search memos..." 
                               class="input"
                               onkeyup="app.memos.searchMemos(this.value)">
                    </div>
                    <div class="input-group">
                        <select id="memo-stage-filter" class="input select" onchange="app.memos.filterByStage(this.value)">
                            <option value="">All Stages</option>
                            <option value="pen">Pending</option>
                            <option value="pos">Postponed</option>
                            <option value="rev">Reviewed</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <select id="memo-draft-filter" class="input select" onchange="app.memos.filterByDraft(this.value)">
                            <option value="">All Memos</option>
                            <option value="false">Published</option>
                            <option value="true">Drafts</option>
                        </select>
                    </div>
                </div>

                <!-- Memos Grid -->
                <div id="memos-content" class="min-h-[400px]">
                    <div class="text-center py-8">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
                        <p class="text-gray-500 mt-4">Loading memos...</p>
                    </div>
                </div>
            </div>
        `;

        await this.loadMemosList();
    }

    async loadMemosList(searchTerm = '', filters = {}) {
        const content = document.getElementById('memos-content');
        
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append('search', searchTerm);
            if (filters.stage) params.append('stage', filters.stage);
            if (filters.draft !== undefined) params.append('draft', filters.draft);

            const url = `${window.CRM_CONFIG.ENDPOINTS.MEMOS}?${params.toString()}`;
            const response = await window.apiClient.get(url);
            
            this.currentMemos = response.results || [];

            if (this.currentMemos.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-16">
                        <div class="text-6xl mb-4">📝</div>
                        <h3 class="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            ${searchTerm ? 'No memos found' : 'No memos yet'}
                        </h3>
                        <p class="text-gray-500 mb-6">
                            ${searchTerm ? `No memos match "${searchTerm}"` : 'Create your first memo to get started'}
                        </p>
                        ${!searchTerm ? `
                            <button onclick="app.memos.showMemoForm()" class="btn btn-primary">
                                Create Memo
                            </button>
                        ` : ''}
                    </div>
                `;
                return;
            }

            // Render memos in a masonry-style grid
            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${this.currentMemos.map(memo => this.renderMemoCard(memo)).join('')}
                </div>
            `;

        } catch (error) {
            console.error('Failed to load memos:', error);
            content.innerHTML = `
                <div class="text-center py-16">
                    <div class="text-6xl mb-4">⚠️</div>
                    <h3 class="text-xl font-semibold text-red-600 mb-2">Failed to load memos</h3>
                    <p class="text-gray-500 mb-6">${error.message || 'Please try again later'}</p>
                    <button onclick="app.memos.loadMemosList()" class="btn btn-primary">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    renderMemoCard(memo) {
        const colors = [
            'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-700',
            'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700',
            'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700',
            'bg-pink-50 border-pink-200 dark:bg-pink-900/20 dark:border-pink-700',
            'bg-purple-50 border-purple-200 dark:bg-purple-900/20 dark:border-purple-700'
        ];
        const colorClass = colors[memo.id % colors.length];

        const stageLabels = {
            'pen': '<span class="badge badge-warning">Pending</span>',
            'pos': '<span class="badge badge-info">Postponed</span>',
            'rev': '<span class="badge badge-success">Reviewed</span>'
        };

        const formattedDate = new Date(memo.creation_date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: new Date(memo.creation_date).getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
        });

        return `
            <div class="card ${colorClass} border-2 p-5 hover:shadow-lg transition-all cursor-pointer transform hover:-translate-y-1" 
                 data-id="${memo.id}"
                 onclick="app.memos.viewMemo(${memo.id})">
                <div class="flex items-start justify-between mb-3">
                    <h3 class="text-lg font-bold text-gray-900 dark:text-white flex-1 line-clamp-2">
                        ${this.escapeHtml(memo.name || 'Untitled')}
                    </h3>
                    <div class="flex gap-2 ml-2">
                        ${memo.draft ? '<span class="badge badge-sm badge-secondary">Draft</span>' : ''}
                        <button class="btn-icon btn-text btn-sm" 
                                onclick="event.stopPropagation(); app.memos.editMemo(${memo.id})"
                                title="Edit">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                ${memo.description ? `
                    <p class="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 mb-4">${this.escapeHtml(memo.description)}</p>
                ` : ''}
                
                <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                    <div class="flex flex-col gap-1">
                        <span>📅 ${formattedDate}</span>
                        ${memo.to_name ? `<span>👤 To: ${this.escapeHtml(memo.to_name)}</span>` : ''}
                    </div>
                    <div class="flex flex-col items-end gap-1">
                        ${stageLabels[memo.stage] || ''}
                        ${memo.review_date ? `<span class="text-xs">Review: ${new Date(memo.review_date).toLocaleDateString()}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    async viewMemo(memoId) {
        try {
            const memo = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}${memoId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'memo-view-modal';
            modal.className = 'modal-overlay fade-in';
            
            const stageLabels = {
                'pen': '<span class="badge badge-warning">Pending</span>',
                'pos': '<span class="badge badge-info">Postponed</span>',
                'rev': '<span class="badge badge-success">Reviewed</span>'
            };

            modal.innerHTML = `
                <div class="modal w-full max-w-4xl scale-in dark:bg-slate-800 dark:text-white">
                    <div class="modal-header">
                        <div class="flex-1">
                            <h3 class="modal-title">${this.escapeHtml(memo.name)}</h3>
                            <div class="flex gap-2 mt-2">
                                ${memo.draft ? '<span class="badge badge-secondary">Draft</span>' : ''}
                                ${stageLabels[memo.stage] || ''}
                            </div>
                        </div>
                        <button class="btn-icon btn-text" onclick="document.getElementById('memo-view-modal').remove()">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="modal-body space-y-6">
                        <!-- Metadata -->
                        <div class="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span class="font-semibold">Owner:</span> ${this.escapeHtml(memo.owner_name || 'N/A')}
                            </div>
                            <div>
                                <span class="font-semibold">To:</span> ${this.escapeHtml(memo.to_name || 'N/A')}
                            </div>
                            <div>
                                <span class="font-semibold">Created:</span> ${new Date(memo.creation_date).toLocaleString()}
                            </div>
                            ${memo.review_date ? `
                                <div>
                                    <span class="font-semibold">Review Date:</span> ${new Date(memo.review_date).toLocaleDateString()}
                                </div>
                            ` : ''}
                        </div>

                        <!-- Description -->
                        ${memo.description ? `
                            <div>
                                <h4 class="font-semibold text-lg mb-2">Description</h4>
                                <div class="prose dark:prose-invert max-w-none">
                                    ${this.nl2br(this.escapeHtml(memo.description))}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Note/Conclusion -->
                        ${memo.note ? `
                            <div>
                                <h4 class="font-semibold text-lg mb-2">Conclusion</h4>
                                <div class="prose dark:prose-invert max-w-none">
                                    ${this.nl2br(this.escapeHtml(memo.note))}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Related Items -->
                        ${memo.task_name || memo.project_name || memo.deal_name ? `
                            <div>
                                <h4 class="font-semibold text-lg mb-2">Related To</h4>
                                <div class="flex flex-wrap gap-2">
                                    ${memo.task_name ? `<span class="badge badge-info">Task: ${this.escapeHtml(memo.task_name)}</span>` : ''}
                                    ${memo.project_name ? `<span class="badge badge-info">Project: ${this.escapeHtml(memo.project_name)}</span>` : ''}
                                    ${memo.deal_name ? `<span class="badge badge-info">Deal: ${this.escapeHtml(memo.deal_name)}</span>` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Tags -->
                        ${memo.tag_names && memo.tag_names.length > 0 ? `
                            <div>
                                <h4 class="font-semibold text-lg mb-2">Tags</h4>
                                <div class="flex flex-wrap gap-2">
                                    ${memo.tag_names.map(tag => `<span class="badge badge-secondary">${this.escapeHtml(tag)}</span>`).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('memo-view-modal').remove()">
                            Close
                        </button>
                        <button type="button" class="btn btn-primary" onclick="app.memos.editMemo(${memoId}); document.getElementById('memo-view-modal').remove();">
                            Edit
                        </button>
                        ${memo.stage === 'pen' ? `
                            <button type="button" class="btn btn-success" onclick="app.memos.markReviewed(${memoId})">
                                Mark Reviewed
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

        } catch (error) {
            console.error('Failed to load memo:', error);
            this.app.showToast('Failed to load memo', 'error');
        }
    }

    async showMemoForm(memoId = null) {
        const isEdit = memoId !== null;
        let memoData = null;

        if (isEdit) {
            try {
                memoData = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}${memoId}/`);
            } catch (error) {
                this.app.showToast('Failed to load memo', 'error');
                return;
            }
        }

        // Load users for the "to" dropdown
        let users = [];
        try {
            const usersResponse = await window.apiClient.get('users/');
            users = usersResponse.results || usersResponse || [];
        } catch (error) {
            console.warn('Failed to load users:', error);
        }

        const modal = document.createElement('div');
        modal.id = 'memo-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-4xl scale-in dark:bg-slate-800 dark:text-white">
                <div class="modal-header">
                    <h3 class="modal-title">${isEdit ? 'Edit' : 'New'} Memo</h3>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-500" id="auto-save-status"></span>
                        <button class="btn-icon btn-text" onclick="document.getElementById('memo-modal').remove()">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="memo-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <label for="name" class="input-label required">Title</label>
                        <input type="text" 
                               id="name" 
                               name="name" 
                               class="input" 
                               placeholder="Memo title"
                               value="${isEdit ? this.escapeHtml(memoData.name) : ''}"
                               required>
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" 
                                  name="description" 
                                  rows="6" 
                                  class="input resize-none" 
                                  placeholder="Memo description...">${isEdit ? this.escapeHtml(memoData.description) : ''}</textarea>
                    </div>
                    
                    <div class="input-group">
                        <label for="note" class="input-label">Conclusion</label>
                        <textarea id="note" 
                                  name="note" 
                                  rows="4" 
                                  class="input resize-none" 
                                  placeholder="Conclusion or notes...">${isEdit ? this.escapeHtml(memoData.note) : ''}</textarea>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="to" class="input-label required">To (Recipient)</label>
                            <select id="to" name="to" class="input select" required>
                                <option value="">Select recipient...</option>
                                ${users.map(user => `
                                    <option value="${user.id}" ${isEdit && memoData.to === user.id ? 'selected' : ''}>
                                        ${this.escapeHtml(user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username)}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                        
                        <div class="input-group">
                            <label for="stage" class="input-label">Stage</label>
                            <select id="stage" name="stage" class="input select">
                                <option value="pen" ${isEdit && memoData.stage === 'pen' ? 'selected' : ''}>Pending</option>
                                <option value="pos" ${isEdit && memoData.stage === 'pos' ? 'selected' : ''}>Postponed</option>
                                <option value="rev" ${isEdit && memoData.stage === 'rev' ? 'selected' : ''}>Reviewed</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="review_date" class="input-label">Review Date</label>
                            <input type="date" 
                                   id="review_date" 
                                   name="review_date" 
                                   class="input"
                                   value="${isEdit && memoData.review_date ? memoData.review_date : ''}">
                        </div>
                        
                        <div class="input-group flex items-center pt-8">
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" 
                                       id="draft" 
                                       name="draft" 
                                       class="mr-2"
                                       ${isEdit && memoData.draft ? 'checked' : ''}>
                                <span class="text-sm">Save as draft</span>
                            </label>
                        </div>
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('memo-modal').remove()">
                        Cancel
                    </button>
                    ${isEdit ? `
                        <button type="button" class="btn btn-danger" onclick="app.memos.deleteMemo(${memoId})">
                            Delete
                        </button>
                    ` : ''}
                    <button type="submit" form="memo-form" class="btn btn-primary">
                        ${isEdit ? 'Update' : 'Create'} Memo
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const memoForm = document.getElementById('memo-form');
        memoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveMemo(memoId);
        });

        // Auto-save to localStorage
        let autoSaveTimeout;
        const autoSave = () => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                const formData = new FormData(memoForm);
                localStorage.setItem('memo_draft', JSON.stringify({
                    id: memoId,
                    name: formData.get('name'),
                    description: formData.get('description'),
                    note: formData.get('note'),
                    timestamp: Date.now()
                }));
                document.getElementById('auto-save-status').textContent = 'Draft saved';
                setTimeout(() => {
                    document.getElementById('auto-save-status').textContent = '';
                }, 2000);
            }, 2000);
        };

        document.getElementById('name').addEventListener('input', autoSave);
        document.getElementById('description').addEventListener('input', autoSave);
        document.getElementById('note').addEventListener('input', autoSave);

        setTimeout(() => document.getElementById('name').focus(), 100);
    }

    async saveMemo(memoId = null) {
        const form = document.getElementById('memo-form');
        const formData = new FormData(form);
        
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            note: formData.get('note'),
            to: parseInt(formData.get('to')),
            stage: formData.get('stage'),
            review_date: formData.get('review_date') || null,
            draft: document.getElementById('draft').checked
        };

        try {
            if (memoId) {
                await window.apiClient.patch(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}${memoId}/`, data);
                this.app.showToast('Memo updated successfully', 'success');
            } else {
                await window.apiClient.post(window.CRM_CONFIG.ENDPOINTS.MEMOS, data);
                this.app.showToast('Memo created successfully', 'success');
            }

            document.getElementById('memo-modal').remove();
            localStorage.removeItem('memo_draft');
            await this.loadMemosList();

        } catch (error) {
            console.error('Failed to save memo:', error);
            this.app.showToast(error.message || 'Failed to save memo', 'error');
        }
    }

    async editMemo(memoId) {
        await this.showMemoForm(memoId);
    }

    async deleteMemo(memoId) {
        if (!confirm('Are you sure you want to delete this memo?')) {
            return;
        }

        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}${memoId}/`);
            this.app.showToast('Memo deleted successfully', 'success');
            document.getElementById('memo-modal')?.remove();
            document.getElementById('memo-view-modal')?.remove();
            await this.loadMemosList();
        } catch (error) {
            console.error('Failed to delete memo:', error);
            this.app.showToast('Failed to delete memo', 'error');
        }
    }

    async markReviewed(memoId) {
        try {
            await window.apiClient.post(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}${memoId}/mark_reviewed/`);
            this.app.showToast('Memo marked as reviewed', 'success');
            document.getElementById('memo-view-modal')?.remove();
            await this.loadMemosList();
        } catch (error) {
            console.error('Failed to mark memo as reviewed:', error);
            this.app.showToast('Failed to update memo', 'error');
        }
    }

    async searchMemos(searchTerm) {
        const stage = document.getElementById('memo-stage-filter')?.value || '';
        const draft = document.getElementById('memo-draft-filter')?.value || '';
        
        await this.loadMemosList(searchTerm, {
            stage: stage || undefined,
            draft: draft || undefined
        });
    }

    async filterByStage(stage) {
        const search = document.getElementById('memo-search')?.value || '';
        const draft = document.getElementById('memo-draft-filter')?.value || '';
        
        await this.loadMemosList(search, {
            stage: stage || undefined,
            draft: draft || undefined
        });
    }

    async filterByDraft(draft) {
        const search = document.getElementById('memo-search')?.value || '';
        const stage = document.getElementById('memo-stage-filter')?.value || '';
        
        await this.loadMemosList(search, {
            stage: stage || undefined,
            draft: draft || undefined
        });
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    nl2br(text) {
        if (!text) return '';
        return text.replace(/\n/g, '<br>');
    }
}
