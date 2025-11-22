// Project management functionality
class ProjectManager {
    constructor(app) {
        this.app = app;
    }

    async loadProjects() {
        const section = document.getElementById('projects-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Projects</h2>
                        <div class="flex space-x-2">
                            <select id="project-status-filter" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                                <option value="">All Projects</option>
                                <option value="true">Active</option>
                                <option value="false">Completed</option>
                            </select>
                            <input type="text" id="project-search" placeholder="Search projects..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                            <button onclick="app.projects.showProjectForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                                Add Project
                            </button>
                        </div>
                    </div>
                </div>
                <div id="projects-content" class="p-6">
                    <div class="htmx-indicator">Loading projects...</div>
                </div>
            </div>
        `;

        document.getElementById('project-search').addEventListener('input', (e) => {
            this.searchProjects(e.target.value);
        });

        document.getElementById('project-status-filter').addEventListener('change', (e) => {
            this.filterByStatus(e.target.value);
        });
        
        if (this.app.token) {
            this.loadProjectsList();
        }
    }

    async loadProjectsList(searchTerm = '', statusFilter = '') {
        try {
            let url = '/projects/?';
            if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
            if (statusFilter) url += `active=${statusFilter}&`;
            
            const projects = await this.app.apiCall(url);
            const content = document.getElementById('projects-content');
            
            if (!projects.results || projects.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            📁
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm || statusFilter ? 'No projects found for your criteria' : 'No projects found'}</p>
                        <button onclick="app.projects.showProjectForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
                            Add Your First Project
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${projects.results.map(project => `
                        <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                             onclick="app.projects.viewProject(${project.id})">
                            <div class="flex items-start justify-between mb-4">
                                <h3 class="text-lg font-semibold text-gray-900 truncate">${project.name}</h3>
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${project.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                    ${project.active ? 'Active' : 'Completed'}
                                </span>
                            </div>
                            
                            <p class="text-gray-600 mb-4 line-clamp-2">${project.description || 'No description'}</p>
                            
                            <div class="space-y-2 mb-4">
                                <div class="flex items-center justify-between text-sm">
                                    <span class="text-gray-500">Stage:</span>
                                    <span class="text-gray-900">${project.stage_name || 'No stage'}</span>
                                </div>
                                
                                ${project.priority ? `
                                    <div class="flex items-center justify-between text-sm">
                                        <span class="text-gray-500">Priority:</span>
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getPriorityColor(project.priority)}">
                                            ${project.priority}
                                        </span>
                                    </div>
                                ` : ''}
                                
                                <div class="flex items-center justify-between text-sm">
                                    <span class="text-gray-500">Due Date:</span>
                                    <span class="text-gray-900 ${this.isDueSoon(project.due_date) ? 'text-red-600 font-medium' : ''}">${project.due_date ? new Date(project.due_date).toLocaleDateString() : 'No due date'}</span>
                                </div>
                                
                                <div class="flex items-center justify-between text-sm">
                                    <span class="text-gray-500">Progress:</span>
                                    <span class="text-gray-900">${this.calculateProgress(project)}%</span>
                                </div>
                            </div>
                            
                            <!-- Progress Bar -->
                            <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                                <div class="bg-primary-600 h-2 rounded-full transition-all duration-300" style="width: ${this.calculateProgress(project)}%"></div>
                            </div>
                            
                            <div class="flex justify-between items-center">
                                <div class="flex items-center space-x-2 text-sm text-gray-500">
                                    <span>Created: ${new Date(project.creation_date).toLocaleDateString()}</span>
                                </div>
                                
                                <div class="flex space-x-1">
                                    <button onclick="event.stopPropagation(); app.projects.editProject(${project.id})" 
                                            class="text-yellow-600 hover:text-yellow-900 text-sm">Edit</button>
                                    <button onclick="event.stopPropagation(); app.projects.deleteProject(${project.id})" 
                                            class="text-red-600 hover:text-red-900 text-sm">Delete</button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            document.getElementById('projects-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading projects</div>';
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
        return diffDays <= 7 && diffDays >= 0;
    }

    calculateProgress(project) {
        // Simple progress calculation based on dates
        if (!project.start_date || !project.due_date) return 0;
        if (!project.active) return 100;
        
        const start = new Date(project.start_date);
        const due = new Date(project.due_date);
        const now = new Date();
        
        if (now < start) return 0;
        if (now > due) return 100;
        
        const total = due - start;
        const elapsed = now - start;
        return Math.round((elapsed / total) * 100);
    }

    searchProjects(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadProjectsList(term, document.getElementById('project-status-filter').value);
        }, 300);
    }

    filterByStatus(status) {
        this.loadProjectsList(document.getElementById('project-search').value, status);
    }

    showProjectForm(projectId = null) {
        const isEdit = projectId !== null;
        const title = isEdit ? 'Edit Project' : 'Add New Project';

        const modal = document.createElement('div');
        modal.id = 'project-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('project-modal').remove()" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="project-form" class="p-6 space-y-4">
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
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
                            <label for="stage" class="block text-sm font-medium text-gray-700 mb-1">Stage</label>
                            <select id="stage" name="stage" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <option value="">Select Stage</option>
                            </select>
                        </div>
                        
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
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label for="start_date" class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                            <input type="date" id="start_date" name="start_date"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
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
                        <button type="button" onclick="document.getElementById('project-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                            ${isEdit ? 'Update' : 'Create'} Project
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Load dropdowns
        this.loadProjectFormDropdowns();

        if (isEdit) {
            this.loadProjectData(projectId);
        }

        document.getElementById('project-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProject(projectId);
        });
    }

    async loadProjectFormDropdowns() {
        try {
            const stages = await this.app.apiCall('/project-stages/');

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

    async loadProjectData(projectId) {
        try {
            const project = await this.app.apiCall(`/projects/${projectId}/`);
            
            const fields = ['name', 'description', 'next_step', 'note', 'start_date', 'due_date', 'next_step_date', 'priority'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && project[field]) {
                    element.value = project[field];
                }
            });

            // Set dropdown
            if (project.stage) document.getElementById('stage').value = project.stage;

            // Set checkboxes
            document.getElementById('active').checked = project.active;
            document.getElementById('remind_me').checked = project.remind_me;

        } catch (error) {
            this.app.showToast('Error loading project data', 'error');
        }
    }

    async saveProject(projectId = null) {
        const formData = new FormData(document.getElementById('project-form'));
        const projectData = Object.fromEntries(formData.entries());
        
        // Convert checkboxes to boolean
        projectData.active = document.getElementById('active').checked;
        projectData.remind_me = document.getElementById('remind_me').checked;
        
        // Remove empty fields
        Object.keys(projectData).forEach(key => {
            if (!projectData[key]) delete projectData[key];
        });

        try {
            const method = projectId ? 'PUT' : 'POST';
            const url = projectId ? `/projects/${projectId}/` : '/projects/';
            
            await this.app.apiCall(url, {
                method: method,
                body: JSON.stringify(projectData)
            });

            document.getElementById('project-modal').remove();
            this.loadProjectsList();
            this.app.showToast(`Project ${projectId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${projectId ? 'updating' : 'creating'} project`, 'error');
        }
    }

    async editProject(projectId) {
        this.showProjectForm(projectId);
    }

    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project?')) {
            return;
        }

        try {
            await this.app.apiCall(`/projects/${projectId}/`, { method: 'DELETE' });
            this.loadProjectsList();
            this.app.showToast('Project deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting project', 'error');
        }
    }

    async viewProject(projectId) {
        try {
            const project = await this.app.apiCall(`/projects/${projectId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'project-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Project Details</h3>
                            <button onclick="document.getElementById('project-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                <h4 class="text-2xl font-bold text-gray-900">${project.name}</h4>
                                <div class="flex items-center space-x-2">
                                    <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${project.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                        ${project.active ? 'Active' : 'Completed'}
                                    </span>
                                    ${project.priority ? `
                                        <span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${this.getPriorityColor(project.priority)}">
                                            Priority: ${project.priority}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                            
                            <!-- Progress Bar -->
                            <div class="mt-4">
                                <div class="flex justify-between text-sm text-gray-600 mb-1">
                                    <span>Progress</span>
                                    <span>${this.calculateProgress(project)}%</span>
                                </div>
                                <div class="w-full bg-gray-200 rounded-full h-3">
                                    <div class="bg-primary-600 h-3 rounded-full transition-all duration-300" style="width: ${this.calculateProgress(project)}%"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Project Information</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Stage</dt>
                                        <dd class="text-sm text-gray-900">${project.stage_name || 'No stage'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Start Date</dt>
                                        <dd class="text-sm text-gray-900">${project.start_date ? new Date(project.start_date).toLocaleDateString() : 'No start date'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Due Date</dt>
                                        <dd class="text-sm text-gray-900 ${this.isDueSoon(project.due_date) ? 'text-red-600 font-medium' : ''}">${project.due_date ? new Date(project.due_date).toLocaleDateString() : 'No due date'}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Next Step Date</dt>
                                        <dd class="text-sm text-gray-900">${project.next_step_date ? new Date(project.next_step_date).toLocaleDateString() : 'No next step date'}</dd>
                                    </div>
                                </dl>
                            </div>
                            
                            <div>
                                <h5 class="text-lg font-medium text-gray-900 mb-4">Status & Dates</h5>
                                <dl class="space-y-3">
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Created</dt>
                                        <dd class="text-sm text-gray-900">${new Date(project.creation_date).toLocaleDateString()}</dd>
                                    </div>
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                        <dd class="text-sm text-gray-900">${new Date(project.update_date).toLocaleDateString()}</dd>
                                    </div>
                                    ${project.closing_date ? `
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Closing Date</dt>
                                            <dd class="text-sm text-gray-900">${new Date(project.closing_date).toLocaleDateString()}</dd>
                                        </div>
                                    ` : ''}
                                    <div>
                                        <dt class="text-sm font-medium text-gray-500">Reminders</dt>
                                        <dd class="text-sm text-gray-900">${project.remind_me ? 'Enabled' : 'Disabled'}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                        
                        ${project.description ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Description</h5>
                                <p class="text-gray-700">${project.description}</p>
                            </div>
                        ` : ''}
                        
                        ${project.next_step ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Next Step</h5>
                                <p class="text-gray-700">${project.next_step}</p>
                            </div>
                        ` : ''}
                        
                        ${project.note ? `
                            <div class="mt-6">
                                <h5 class="text-lg font-medium text-gray-900 mb-3">Notes</h5>
                                <p class="text-gray-700">${project.note}</p>
                            </div>
                        ` : ''}
                        
                        <div class="mt-8 flex justify-end space-x-3">
                            <button onclick="app.projects.editProject(${project.id}); document.getElementById('project-view-modal').remove();" 
                                    class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                                Edit Project
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading project details', 'error');
        }
    }
}