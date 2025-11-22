// Task management functionality
class TaskManager {
    constructor(app) {
        this.app = app;
    }

    async loadTasks() {
        const section = document.getElementById('tasks-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow dark:bg-slate-800">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Tasks</h2>
                        <div class="flex space-x-2">
                            <select id="task-status-filter" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                                <option value="">All Tasks</option>
                                <option value="true">Active</option>
                                <option value="false">Completed</option>
                            </select>
                            <input type="text" id="task-search" placeholder="Search tasks..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                            <button onclick="app.tasks.showTaskForm()" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                                Add Task
                            </button>
                        </div>
                    </div>
                </div>
                <div id="tasks-content" class="p-6">
                    <div class="htmx-indicator">Loading tasks...</div>
                </div>
            </div>
        `;

        document.getElementById('task-search').addEventListener('input', (e) => {
            this.searchTasks(e.target.value);
        });

        document.getElementById('task-status-filter').addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });
        
        if (this.app.token) {
            this.loadTasksList();
        }
    }

    async loadTasksList(searchTerm = '', statusFilter = '') {
        try {
            let url = 'v1/tasks/?';
            if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
            if (statusFilter) url += `active=${statusFilter}&`;
            
            const tasks = await this.app.apiCall(url);
            const content = document.getElementById('tasks-content');
            
            if (!tasks.results || tasks.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            ✓
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm || statusFilter ? 'No tasks found for your criteria' : 'No tasks found'}</p>
                        <button onclick="app.tasks.showTaskForm()" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                            Add Your First Task
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="space-y-4">
                    ${tasks.results.map(task => `
                        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow dark:bg-slate-800 dark:border-slate-700">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center space-x-3">
                                        <h3 class="text-lg font-medium text-gray-900">${task.name}</h3>
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${task.active ? 'bg-success bg-opacity-20 text-success' : 'bg-gray-100 text-gray-800'}">
                                            ${task.active ? 'Active' : 'Completed'}
                                        </span>
                                        ${task.priority ? `
                                            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getPriorityColor(task.priority)}">
                                                Priority: ${task.priority}
                                            </span>
                                        ` : ''}
                                    </div>
                                    
                                    <p class="text-gray-600 mt-1">${task.description || 'No description'}</p>
                                    
                                    <div class="mt-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                                        <div>
                                            <span class="text-gray-500">Project:</span>
                                            <span class="ml-1 text-gray-900">${task.project_name || 'No project'}</span>
                                        </div>
                                        <div>
                                            <span class="text-gray-500">Stage:</span>
                                            <span class="ml-1 text-gray-900">${task.stage_name || 'No stage'}</span>
                                        </div>
                                        <div>
                                            <span class="text-gray-500">Due Date:</span>
                                            <span class="ml-1 text-gray-900 ${this.isDueSoon(task.due_date) ? 'text-danger font-medium' : ''}">${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</span>
                                        </div>
                                        <div>
                                            <span class="text-gray-500">Next Step:</span>
                                            <span class="ml-1 text-gray-900">${task.next_step_date ? new Date(task.next_step_date).toLocaleDateString() : 'No next step'}</span>
                                        </div>
                                    </div>
                                    
                                    ${task.next_step ? `
                                        <div class="mt-3">
                                            <span class="text-gray-500">Next Step:</span>
                                            <span class="ml-1 text-gray-900">${task.next_step}</span>
                                        </div>
                                    ` : ''}
                                </div>
                                
                                <div class="flex flex-col space-y-2 ml-4">
                                    <button onclick="app.tasks.viewTask(${task.id})" class="text-primary hover:opacity-90 text-sm">View</button>
                                    <button onclick="app.tasks.editTask(${task.id})" class="text-warning hover:opacity-90 text-sm">Edit</button>
                                    <button onclick="app.tasks.deleteTask(${task.id})" class="text-danger hover:opacity-90 text-sm">Delete</button>
                                    ${task.active ? `
                                        <button onclick="app.tasks.markCompleted(${task.id})" class="text-success hover:opacity-90 text-sm">Complete</button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${tasks.count > tasks.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-gray-500">
                            Showing ${tasks.results.length} of ${tasks.count} tasks
                        </div>
                        <div class="flex space-x-2">
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Previous</button>
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;
        } catch (error) {
            document.getElementById('tasks-content').innerHTML = '<div class="text-danger text-center py-4">Error loading tasks</div>';
        }
    }

    getPriorityColor(priority) {
        // Normalize priority to support both numeric (1-5) and string values (high|medium|low)
        const toKey = (p) => {
            if (p == null) return null;
            if (typeof p === 'number') return p;
            const s = String(p).trim().toLowerCase();
            if (s === 'high') return 1;
            if (s === 'medium') return 3;
            if (s === 'low') return 5;
            const n = Number(s);
            return Number.isFinite(n) ? n : null;
        };
        const key = toKey(priority);
        const colors = {
            1: 'bg-danger bg-opacity-20 text-danger',
            2: 'bg-warning bg-opacity-20 text-warning',
            3: 'bg-yellow-400 bg-opacity-20 text-yellow-400',
            4: 'bg-primary bg-opacity-20 text-primary',
            5: 'bg-gray-100 text-gray-800'
        };
        return (key && colors[key]) ? colors[key] : 'bg-gray-100 text-gray-800';
    }

    isDueSoon(dueDate) {
        if (!dueDate) return false;
        const due = new Date(dueDate);
        const now = new Date();
        const diffTime = due - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays <= 3 && diffDays >= 0;
    }

    searchTasks(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadTasksList(term, document.getElementById('task-status-filter').value);
        }, 300);
    }

    filterByStatus(status) {
        this.loadTasksList(document.getElementById('task-search').value, status);
    }



    async loadTaskFormDropdowns() {
        try {
            const [projects, stages] = await Promise.all([
                window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.PROJECTS),
                window.apiClient.get('v1/task-stages/')
            ]);

            // Load projects
            const projectSelect = document.getElementById('project');
            if (projects.results) {
                projects.results.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = project.name;
                    projectSelect.appendChild(option);
                });
            }

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
        } catch (error) {
            console.error('Error loading form dropdowns:', error);
        }
    }

    async loadTaskData(taskId) {
        try {
            const task = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.TASKS}${taskId}/`);
            
            const fields = ['name', 'description', 'next_step', 'note', 'due_date', 'next_step_date', 'priority'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && task[field]) {
                    element.value = task[field];
                }
            });

            // Set dropdowns
            if (task.project) document.getElementById('project').value = task.project;
            if (task.stage) document.getElementById('stage').value = task.stage;

            // Set checkboxes
            document.getElementById('active').checked = task.active;
            document.getElementById('remind_me').checked = task.remind_me;

        } catch (error) {
            this.app.showToast('Error loading task data', 'error');
        }
    }

    async saveTask(taskId = null) {
        const formData = new FormData(document.getElementById('task-form'));
        const taskData = Object.fromEntries(formData.entries());
        
        // Convert checkboxes to boolean
        taskData.active = document.getElementById('active').checked;
        taskData.remind_me = document.getElementById('remind_me').checked;
        
        // Remove empty fields
        Object.keys(taskData).forEach(key => {
            if (!taskData[key]) delete taskData[key];
        });

        try {
            const method = taskId ? 'PUT' : 'POST';
            const url = taskId ? `${window.CRM_CONFIG.ENDPOINTS.TASKS}${taskId}/` : window.CRM_CONFIG.ENDPOINTS.TASKS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(taskData)
            });

            document.getElementById('task-modal').remove();
            this.loadTasksList();
            this.app.showToast(`Task ${taskId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${taskId ? 'updating' : 'creating'} task`, 'error');
        }
    }

    async editTask(taskId) {
        this.showTaskForm(taskId);
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.TASKS}${taskId}/`);
            this.loadTasksList();
            this.app.showToast('Task deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting task', 'error');
        }
    }

    async markCompleted(taskId) {
        try {
            // Get completed stage
            const stages = await window.apiClient.get('v1/task-stages/');
            const completedStage = stages.results?.find(stage => stage.done === true);
            
            if (!completedStage) {
                this.app.showToast('No completed stage found', 'error');
                return;
            }

            await window.apiClient.patch(`${window.CRM_CONFIG.ENDPOINTS.TASKS}${taskId}/`, {
                stage: completedStage.id,
                active: false
            });

            this.loadTasksList();
            this.app.showToast('Task marked as completed', 'success');
        } catch (error) {
            this.app.showToast('Error completing task', 'error');
        }
    }

    async viewTask(taskId) {
        try {
            const task = await this.app.apiCall(`/v1/tasks/${taskId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'task-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Task Details</h3>
                            <button onclick="document.getElementById('task-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                <h4 class="text-2xl font-bold text-gray-900">${task.name}</h4>
                                <div class="flex items-center space-x-2">
                                    <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${task.active ? 'bg-success bg-opacity-20 text-success' : 'bg-gray-100 text-gray-800'}">
                                        ${task.active ? 'Active' : 'Completed'}
                                    </span>
                                    ${task.priority ? `
                                        <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${this.getPriorityColor(task.priority)}">
                                            Priority: ${task.priority}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Task Information</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Project</dt>
                                        <dd class="text-sm text-gray-900">${task.project_name || 'No project'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Stage</dt>
                                        <dd class="text-sm text-gray-900">${task.stage_name || 'No stage'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Due Date</dt>
                                        <dd class="text-sm text-gray-900 ${this.isDueSoon(task.due_date) ? 'text-danger font-medium' : ''}">${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Next Step Date</dt>
                                        <dd class="text-sm text-gray-900">${task.next_step_date ? new Date(task.next_step_date).toLocaleDateString() : 'No next step date'}</dd>
                                    </div>
                                </dl>
                            </div>
                            
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Status & Dates</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Created</dt>
                                        <dd class="text-sm text-gray-900">${new Date(task.creation_date).toLocaleDateString()}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                        <dd class="text-sm text-gray-900">${new Date(task.update_date).toLocaleDateString()}</dd>
                                    </div>
                                    ${task.closing_date ? `
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Closing Date</dt>
                                            <dd class="text-sm text-gray-900">${new Date(task.closing_date).toLocaleDateString()}</dd>
                                        </div>
                                    ` : ''}
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Reminders</dt>
                                        <dd class="text-sm text-gray-900">${task.remind_me ? 'Enabled' : 'Disabled'}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                        
                        ${task.description ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Description</h5>
                                <p class="text-gray-700">${task.description}</p>
                            </div>
                        ` : ''}
                        
                        ${task.next_step ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Next Step</h5>
                                <p class="text-gray-700">${task.next_step}</p>
                            </div>
                        ` : ''}
                        
                        ${task.note ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Notes</h5>
                                <p class="text-gray-700">${task.note}</p>
                            </div>
                        ` : ''}
                        
                        <div class="mt-8 flex justify-end space-x-3">
                            ${task.active ? `
                                <button onclick="app.tasks.markCompleted(${task.id}); document.getElementById('task-view-modal').remove();" 
                                        class="px-4 py-2 bg-success text-white rounded-md hover:bg-opacity-90">
                                    Mark Completed
                                </button>
                            ` : ''}
                            <button onclick="app.tasks.editTask(${task.id}); document.getElementById('task-view-modal').remove();" 
                                    class="px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90">
                                Edit Task
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading task details', 'error');
        }
    }
}
/* ===== Merged UX patches from tasks-ux.js ===== */

/**
 * UX Enhancements for Tasks Module
 */

if (typeof TaskManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadTasksList
    const originalLoadTasksList = TaskManager.prototype.loadTasksList;
    TaskManager.prototype.loadTasksList = async function(searchTerm = '') {
        const content = document.getElementById('tasks-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'list', 8);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const tasks = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.TASKS}?${searchParam}`);
            
            if (!tasks.results || tasks.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '✅',
                    title: searchTerm ? 'No tasks found' : 'No tasks yet',
                    description: searchTerm 
                        ? `No tasks match "${searchTerm}"`
                        : 'Stay organized by creating your first task',
                    actionLabel: 'Create Task',
                    actionHandler: 'app.tasks.showTaskForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("task-search").value=""; app.tasks.loadTasksList()'
                    } : null
                });
                return;
            }

            // Group tasks by status
            const tasksByStatus = {
                pending: tasks.results.filter(t => !t.completed),
                completed: tasks.results.filter(t => t.completed)
            };

            content.innerHTML = `
                <div class="space-y-6">
                    <!-- Pending Tasks -->
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold text-surface-900">
                                Pending Tasks
                                <span class="badge badge-primary ml-2">${tasksByStatus.pending.length}</span>
                            </h3>
                        </div>
                        <div class="space-y-3">
                            ${tasksByStatus.pending.map(task => this.renderTaskCard(task)).join('')}
                        </div>
                    </div>
                    
                    <!-- Completed Tasks -->
                    ${tasksByStatus.completed.length > 0 ? `
                        <div>
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="text-lg font-semibold text-surface-600">
                                    Completed Tasks
                                    <span class="badge badge-secondary ml-2">${tasksByStatus.completed.length}</span>
                                </h3>
                            </div>
                            <div class="space-y-3">
                                ${tasksByStatus.completed.map(task => this.renderTaskCard(task)).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;

            // Enable inline checkbox toggle
            this.setupInlineTaskToggle();

        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load tasks',
                message: 'Unable to fetch tasks from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.tasks.loadTasksList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Render task card
    TaskManager.prototype.renderTaskCard = function(task) {
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        const isOverdue = dueDate && dueDate < new Date() && !task.completed;
        const dueDateClass = isOverdue ? 'text-error-600' : 'text-surface-600';

        return `
            <div class="card p-4 ${task.completed ? 'opacity-60' : ''}" data-id="${task.id}">
                <div class="flex items-start gap-4">
                    <input type="checkbox" 
                           class="checkbox mt-1 task-checkbox" 
                           ${task.completed ? 'checked' : ''}
                           data-task-id="${task.id}">
                    
                    <div class="flex-1 min-w-0">
                        <h4 class="font-semibold text-surface-900 ${task.completed ? 'line-through' : ''}">
                            ${task.title}
                        </h4>
                        ${task.description ? `
                            <p class="text-sm text-surface-600 mt-1">${task.description}</p>
                        ` : ''}
                        
                        <div class="flex items-center gap-4 mt-3 text-sm">
                            ${dueDate ? `
                                <div class="flex items-center gap-1 ${dueDateClass}">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                    ${this.formatDate(task.due_date)}
                                    ${isOverdue ? '(Overdue)' : ''}
                                </div>
                            ` : ''}
                            
                            ${task.priority ? `
                                <span class="badge ${this.getPriorityBadgeClass(task.priority)}">
                                    ${task.priority}
                                </span>
                            ` : ''}
                            
                            ${task.assigned_to_name ? `
                                <div class="flex items-center gap-1 text-surface-600">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                    </svg>
                                    ${task.assigned_to_name}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="flex gap-2">
                        <button data-action="tasks.editTask" data-id="${task.id}" class="btn btn-text btn-sm">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button data-action="tasks.deleteTask" data-id="${task.id}" class="btn btn-text btn-sm text-error-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    };

    // Format date
    TaskManager.prototype.formatDate = function(dateString) {
        const date = new Date(dateString);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (date.toDateString() === tomorrow.toDateString()) {
            return 'Tomorrow';
        }
        
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    // Priority badge class
    TaskManager.prototype.getPriorityBadgeClass = function(priority) {
        if (priority == null) return 'badge-secondary';
        const s = String(priority).trim().toLowerCase();
        const classes = {
            '1': 'badge-error',
            '2': 'badge-warning',
            '3': 'badge-warning',
            '4': 'badge-secondary',
            '5': 'badge-secondary',
            'high': 'badge-error',
            'medium': 'badge-warning',
            'low': 'badge-secondary'
        };
        return classes[s] || 'badge-secondary';
    };

    // Setup inline task toggle
    TaskManager.prototype.setupInlineTaskToggle = function() {
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const taskId = e.target.dataset.taskId;
                const completed = e.target.checked;
                
                // Optimistic update
                const card = e.target.closest('.card');
                card.style.opacity = completed ? '0.6' : '1';
                const title = card.querySelector('h4');
                if (completed) {
                    title.classList.add('line-through');
                } else {
                    title.classList.remove('line-through');
                }

                try {
                    await window.apiClient.request(`${window.CRM_CONFIG.ENDPOINTS.TASKS}${taskId}/`, {
                        method: 'PATCH',
                        body: JSON.stringify({ completed })
                    });
                    
                    if (window.app) {
                        window.app.showToast(
                            completed ? 'Task completed! 🎉' : 'Task reopened',
                            'success'
                        );
                    }
                } catch (error) {
                    // Rollback
                    e.target.checked = !completed;
                    card.style.opacity = completed ? '1' : '0.6';
                    if (completed) {
                        title.classList.remove('line-through');
                    } else {
                        title.classList.add('line-through');
                    }
                    
                    if (window.app) {
                        window.app.showToast('Failed to update task', 'error');
                    }
                }
            });
        });
    };

    // Enhanced showTaskForm with progressive disclosure
    const originalShowTaskForm = TaskManager.prototype.showTaskForm;
    TaskManager.prototype.showTaskForm = function(taskId = null) {
        const isEdit = taskId !== null;
        
        const modal = document.createElement('div');
        modal.id = 'task-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${isEdit ? 'Edit' : 'Create'} Task</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('task-modal').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="task-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <label for="title" class="input-label">Task Title *</label>
                        <input type="text" id="title" name="title" required class="input" placeholder="e.g., Follow up with client">
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="due_date" class="input-label">Due Date</label>
                            <input type="date" id="due_date" name="due_date" class="input">
                        </div>
                        <div class="input-group">
                            <label for="priority" class="input-label">Priority</label>
                            <select id="priority" name="priority" class="input select">
                                <option value="low">Low</option>
                                <option value="medium" selected>Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Advanced fields -->
                    <div class="input-group" data-advanced="true">
                        <label for="assigned_to" class="input-label">Assigned To</label>
                        <select id="assigned_to" name="assigned_to" class="input select">
                            <option value="">Select user...</option>
                        </select>
                    </div>
                    
                    <div class="input-group" data-advanced="true">
                        <label for="related_to" class="input-label">Related To</label>
                        <select id="related_to" name="related_to" class="input select">
                            <option value="">Select item...</option>
                        </select>
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('task-modal').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="task-form" class="btn btn-primary">
                        ${isEdit ? 'Update' : 'Create'} Task
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const taskForm = document.getElementById('task-form');

        // Progressive disclosure
        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(taskForm);
        }

        if (isEdit) {
            this.loadTaskData(taskId);
        }

        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTask(taskId);
        });

        setTimeout(() => document.getElementById('title').focus(), 100);
    };

    // Setup search progress
    const originalLoadTasks = TaskManager.prototype.loadTasks;
    TaskManager.prototype.loadTasks = function() {
        originalLoadTasks.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('task-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadTasksList(term);
                });
            }
        }, 100);
    };
}
