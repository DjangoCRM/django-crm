// Memo management functionality
class MemoManager {
    constructor(app) {
        this.app = app;
    }

    async loadMemos() {
        const section = document.getElementById('memos-section');
        section.innerHTML = `
            <div class=\"bg-white rounded-lg shadow p-6 dark:bg-slate-800\">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">Memos</h2>
                <p class="text-gray-600">Memo functionality will be implemented based on the memo models found in the system.</p>
                <div class="mt-4">
                    <button class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                        Add Memo
                    </button>
                </div>
            </div>
        `;
    }
}
/* ===== Merged UX patches from memos-ux.js ===== */

/**
 * UX Enhancements for Memos Module
 */

if (typeof MemoManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadMemosList
    const originalLoadMemosList = MemoManager.prototype.loadMemosList;
    MemoManager.prototype.loadMemosList = async function(searchTerm = '') {
        const content = document.getElementById('memos-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'cards', 6);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const memos = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.MEMOS}?${searchParam}`);
            
            if (!memos.results || memos.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '📝',
                    title: searchTerm ? 'No memos found' : 'No memos yet',
                    description: searchTerm 
                        ? `No memos match "${searchTerm}"`
                        : 'Capture important notes and ideas',
                    actionLabel: 'Create Memo',
                    actionHandler: 'app.memos.showMemoForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("memo-search").value=""; app.memos.loadMemosList()'
                    } : null
                });
                return;
            }

            // Masonry-style grid for memos
            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${memos.results.map(memo => this.renderMemoCard(memo)).join('')}
                </div>
            `;

        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load memos',
                message: 'Unable to fetch memos from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.memos.loadMemosList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Render memo card (like sticky note)
    MemoManager.prototype.renderMemoCard = function(memo) {
        const colors = [
            'bg-yellow-50 border-yellow-200',
            'bg-blue-50 border-blue-200',
            'bg-green-50 border-green-200',
            'bg-pink-50 border-pink-200',
            'bg-purple-50 border-purple-200'
        ];
        const colorIndex = parseInt(memo.id) % colors.length;
        const colorClass = colors[colorIndex];

        return `
            <div class="card ${colorClass} p-6 hover:shadow-medium transition-all cursor-pointer" 
                 data-id="${memo.id}"
                 onclick="app.memos.viewMemo('${memo.id}')">
                <div class="flex items-start justify-between mb-3">
                    <h3 class="text-lg font-semibold text-surface-900 flex-1 line-clamp-2">
                        ${memo.title || 'Untitled'}
                    </h3>
                    <button class="btn-icon btn-text btn-sm" 
                            onclick="event.stopPropagation(); app.memos.editMemo('${memo.id}')">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                </div>
                
                ${memo.content ? `
                    <p class="text-sm text-surface-700 line-clamp-4 mb-4">${memo.content}</p>
                ` : ''}
                
                <div class="flex items-center justify-between text-xs text-surface-500">
                    <span>${new Date(memo.creation_date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        year: memo.creation_date.startsWith(new Date().getFullYear().toString()) ? undefined : 'numeric'
                    })}</span>
                    
                    ${memo.category ? `
                        <span class="badge badge-sm badge-secondary">${memo.category}</span>
                    ` : ''}
                </div>
            </div>
        `;
    };

    // Enhanced showMemoForm with auto-save
    const originalShowMemoForm = MemoManager.prototype.showMemoForm;
    MemoManager.prototype.showMemoForm = function(memoId = null) {
        const isEdit = memoId !== null;
        
        const modal = document.createElement('div');
        modal.id = 'memo-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-3xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${isEdit ? 'Edit' : 'New'} Memo</h3>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-surface-500" id="auto-save-status"></span>
                        <button class="btn-icon btn-text" onclick="document.getElementById('memo-modal').remove()">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="memo-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <input type="text" 
                               id="title" 
                               name="title" 
                               class="input text-2xl font-semibold border-0 border-b border-surface-200 rounded-none px-0" 
                               placeholder="Title">
                    </div>
                    
                    <div class="input-group">
                        <textarea id="content" 
                                  name="content" 
                                  rows="12" 
                                  class="input border-0 px-0 resize-none focus:ring-0" 
                                  placeholder="Start writing..."></textarea>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="category" class="input-label">Category</label>
                            <select id="category" name="category" class="input select">
                                <option value="">None</option>
                                <option value="idea">Idea</option>
                                <option value="note">Note</option>
                                <option value="todo">To-Do</option>
                                <option value="reminder">Reminder</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label for="related_to" class="input-label">Related To</label>
                            <select id="related_to" name="related_to" class="input select">
                                <option value="">None</option>
                            </select>
                        </div>
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('memo-modal').remove()">
                        Close
                    </button>
                    <button type="submit" form="memo-form" class="btn btn-primary">
                        Save Memo
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const memoForm = document.getElementById('memo-form');
        
        // Auto-save draft (debounced)
        let autoSaveTimeout;
        const autoSave = () => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                this.saveDraft(memoId);
                document.getElementById('auto-save-status').textContent = 'Draft saved';
                setTimeout(() => {
                    document.getElementById('auto-save-status').textContent = '';
                }, 2000);
            }, 2000);
        };

        document.getElementById('title').addEventListener('input', autoSave);
        document.getElementById('content').addEventListener('input', autoSave);

        if (isEdit) {
            this.loadMemoData(memoId);
        }

        memoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveMemo(memoId);
        });

        setTimeout(() => document.getElementById('title').focus(), 100);
    };

    // Save draft to localStorage
    MemoManager.prototype.saveDraft = function(memoId) {
        const title = document.getElementById('title').value;
        const content = document.getElementById('content').value;
        
        if (!title && !content) return;
        
        localStorage.setItem('memo_draft', JSON.stringify({
            id: memoId,
            title,
            content,
            timestamp: Date.now()
        }));
    };

    // Setup search progress
    const originalLoadMemos = MemoManager.prototype.loadMemos;
    MemoManager.prototype.loadMemos = function() {
        originalLoadMemos.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('memo-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadMemosList(term);
                });
            }
        }, 100);
    };
}
