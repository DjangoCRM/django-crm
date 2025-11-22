// Task management functionality
class TaskManager {
    constructor(app) {
        this.app = app;
    }

    async loadTasks() {
        const section = document.getElementById('tasks-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Tasks</h2>
                        <div class="flex space-x-2">
                            <select id="task-status-filter" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                                <option value="">All Tasks</option>
                                <option value="true">Active</option>
                                <option value="false">Completed</option>
                            </select>
                            <input type="text" id="task-search" placeholder="Search tasks..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                            <button onclick="app.tasks.showTaskForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
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
            let url = '/tasks/?';
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
                        <button onclick="app.tasks.showTaskForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                            Add Your First Task
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="space-y-4">
                    ${tasks.results.map(task => `
                        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center space-x-3">
                                        <h3 class="text-lg font-medium text-gray-900">${task.name}</h3>
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${task.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
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
                                            <span class="ml-1 text-gray-900 ${this.isDueSoon(task.due_date) ? 'text-red-600 font-medium' : ''}">${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</span>
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
                                    <button onclick="app.tasks.viewTask(${task.id})" class="text-primary-600 hover:text-primary-900 text-sm">View</button>
                                    <button onclick="app.tasks.editTask(${task.id})" class="text-yellow-600 hover:text-yellow-900 text-sm">Edit</button>
                                    <button onclick="app.tasks.deleteTask(${task.id})" class="text-red-600 hover:text-red-900 text-sm">Delete</button>
                                    ${task.active ? `
                                        <button onclick="app.tasks.markCompleted(${task.id})" class="text-green-600 hover:text-green-900 text-sm">Complete</button>
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
            document.getElementById('tasks-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading tasks</div>';
        }
    }

    getPriorityColor(priority) {
        const colors = {
            1: 'bg-red-100 text-red-800',
            2: 'bg-orange-100 text-orange-800',
            3: 'bg-yellow-100 text-yellow-800',
            4: 'bg-blue-100 text-blue-800',
            5: 'bg-gray-100 text-gray-800'
        };
        return colors[priority] || 'bg-gray-100 text-gray-800';
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

    showTaskForm(taskId = null) {
        const isEdit = taskId !== null;
        const title = isEdit ? 'Edit Task' : 'Add New Task';

        const modal = document.createElement('div');
        modal.id = 'task-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('task-modal').remove()" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="task-form" class="p-6 space-y-4">
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Task Name *</label>
                        <input type="text" id="name" name="name" required
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea id="description" name="description" rows="3"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="project" class="block text-sm font-medium text-gray-700 mb-1">Project</label>
                            <select id="project" name="project" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Project</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="stage" class="block text-sm font-medium text-gray-700 mb-1">Stage</label>
                            <select id="stage" name="stage" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Stage</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="priority" class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                            <select id="priority" name="priority" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Priority</option>
                                <option value="1">High (1)</option>
                                <option value="2">Medium-High (2)</option>
                                <option value="3">Medium (3)</option>
                                <option value="4">Medium-Low (4)</option>
                                <option value="5">Low (5)</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="due_date" class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                            <input type="date" id="due_date" name="due_date"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        
                        <div>
                            <label for="next_step_date" class="block text-sm font-medium text-gray-700 mb-1">Next Step Date</label>
                            <input type="date" id="next_step_date" name="next_step_date"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                    </div>
                    
                    <div>
                        <label for="next_step" class="block text-sm font-medium text-gray-700 mb-1">Next Step</label>
                        <input type="text" id="next_step" name="next_step"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    
                    <div>
                        <label for="note" class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                        <textarea id="note" name="note" rows="2"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                    </div>
                    
                    <div class="flex items-center space-x-6">
                        <div class="flex items-center">
                            <input type="checkbox" id="active" name="active" checked
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="active" class="ml-2 block text-sm text-gray-900">Active</label>
                        </div>
                        <div class="flex items-center">
                            <input type="checkbox" id="remind_me" name="remind_me"
                                   class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                            <label for="remind_me" class="ml-2 block text-sm text-gray-900">Remind me</label>
                        </div>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="document.getElementById('task-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                            ${isEdit ? 'Update' : 'Create'} Task
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Load dropdowns
        this.loadTaskFormDropdowns();

        if (isEdit) {
            this.loadTaskData(taskId);
        }

        document.getElementById('task-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTask(taskId);
        });
    }

    async loadTaskFormDropdowns() {
        try {
            const [projects, stages] = await Promise.all([
                this.app.apiCall('/v1/projects/'),
                this.app.apiCall('/v1/task-stages/')
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
            const task = await this.app.apiCall(`/v1/tasks/${taskId}/`);
            
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
            const url = taskId ? `/tasks/${taskId}/` : '/tasks/';
            
            await this.app.apiCall(url, {
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
            await this.app.apiCall(`/v1/tasks/${taskId}/`, { method: 'DELETE' });
            this.loadTasksList();
            this.app.showToast('Task deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting task', 'error');
        }
    }

    async markCompleted(taskId) {
        try {
            // Get completed stage
            const stages = await this.app.apiCall('/v1/task-stages/');
            const completedStage = stages.results?.find(stage => stage.done === true);
            
            if (!completedStage) {
                this.app.showToast('No completed stage found', 'error');
                return;
            }

            await this.app.apiCall(`/v1/tasks/${taskId}/`, {
                method: 'PATCH',
                body: JSON.stringify({
                    stage: completedStage.id,
                    active: false
                })
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
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
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
                                    <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${task.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
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
                                        <dd class="text-sm text-gray-900 ${this.isDueSoon(task.due_date) ? 'text-red-600 font-medium' : ''}">${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</dd>
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
                                        class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600">
                                    Mark Completed
                                </button>
                            ` : ''}
                            <button onclick="app.tasks.editTask(${task.id}); document.getElementById('task-view-modal').remove();" 
                                    class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
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