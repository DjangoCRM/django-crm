// Project management functionality
class ProjectManager {
    selected = new Set();
    async prompt(text, def='') {
        const v = window.prompt(text, def);
        if (v === null) throw new Error('cancelled');
        return v.trim();
    }
    constructor(app) {
        this.app = app;
    }

    async loadProjects() {
        this.selected = new Set();
        const section = document.getElementById('projects-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow dark:bg-slate-800">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Projects</h2>
                        <div class="flex space-x-2">
                           <select id="project-sort" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                               <option value="-creation_date">Newest</option>
                               <option value="creation_date">Oldest</option>
                               <option value="due_date">Due date ↑</option>
                               <option value="-due_date">Due date ↓</option>
                               <option value="name">Name A→Z</option>
                               <option value="-name">Name Z→A</option>
                           </select>
                           <button id="project-export" class="bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-2 rounded-lg">Export CSV</button>
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
                <div class="px-6 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                   <div class="flex items-center space-x-3">
                       <label class="inline-flex items-center space-x-2">
                           <input id="projects-select-all" type="checkbox" class="rounded" />
                           <span class="text-sm text-gray-600">Select all</span>
                       </label>
                       <div class="flex items-center space-x-2">
                           <button onclick="app.projects.openBulkAssignDialog()" class="px-3 py-1.5 bg-blue-600 text-white rounded text-sm">Bulk Assign</button>
                           <button onclick="app.projects.openBulkTagDialog()" class="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm">Bulk Tag</button>
                       </div>
                   </div>
                   <div class="text-sm text-gray-500">Selected: <span id="projects-selected-count">0</span></div>
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
        
        document.getElementById('project-sort').addEventListener('change', (e)=>{ this.loadProjectsList(document.getElementById('project-search').value, document.getElementById('project-status-filter').value); });
        document.getElementById('project-export').addEventListener('click', ()=> this.exportProjects());
        // Select all
        document.getElementById('projects-select-all').addEventListener('change', (e) => {
            const check = e.target.checked;
            const boxes = document.querySelectorAll('#projects-content input[type="checkbox"]');
            boxes.forEach(b => { b.checked = check; const id = Number((b.getAttribute('onchange')||'').match(/toggleSelected\((\d+)/)?.[1]); if (id) this.toggleSelected(id, check); });
        });

        if (this.app.token) {
            this.loadProjectsList();
        }
    }

    async loadProjectsList(searchTerm = '', statusFilter = '') {
        try {
            let url = '/projects/?';
            if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
            const ordering = document.getElementById('project-sort')?.value;
            if (ordering) url += `ordering=${encodeURIComponent(ordering)}&`;
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
                        <div class=\"bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800 dark:border-slate-700\"
                             onclick="app.projects.viewProject(${project.id})">
                            <div class=\"flex items-start justify-between\">
                                <label onclick=\"event.stopPropagation();\" class=\"inline-flex items-center space-x-2\">
                                    <input type=\"checkbox\" ${this.selected.has(project.id)?'checked':''} onchange=\"app.projects.toggleSelected(${project.id}, this.checked)\" class=\"rounded\" />
                                </label>
                                ${project.active ? `<span class="px-2 py-0.5 text-xs rounded bg-emerald-100 text-emerald-700">Active</span>` : `<span class="px-2 py-0.5 text-xs rounded bg-gray-200 text-gray-700">Done</span>`}
                            </div>
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
                                    <button onclick="event.stopPropagation(); app.projects.completeProject(${project.id})" 
                                            class="text-green-600 hover:text-green-900 text-sm">Complete</button>
                                    <button onclick="event.stopPropagation(); app.projects.reopenProject(${project.id})" 
                                            class="text-blue-600 hover:text-blue-900 text-sm">Reopen</button>
                                    <button onclick="event.stopPropagation(); app.projects.assignProject(${project.id})" 
                                            class="text-indigo-600 hover:text-indigo-900 text-sm">Assign</button>
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
                <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
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

    toggleSelected(id, checked) {
        if (checked) this.selected.add(id); else this.selected.delete(id);
        const el = document.getElementById('projects-selected-count');
        if (el) el.textContent = this.selected.size;
    }

    openBulkAssignDialog = async () => {
        if (!this.selected.size) return this.app.showToast('Nothing selected','warning');
        const modal = this.makeModal(`
            <h3 class=\"text-lg font-semibold mb-3\">Bulk Assign</h3>
            <input id=\"proj-bulk-owner\" type=\"number\" placeholder=\"User ID\" class=\"w-full border rounded px-3 py-2 mb-4\"/>
            <div class=\"flex justify-end space-x-2\">
                <button class=\"px-3 py-1 bg-gray-200 rounded\" onclick=\"this.closest('.fixed').remove()\">Cancel</button>
                <button class=\"px-3 py-1 bg-blue-600 text-white rounded\" onclick=\"app.projects.bulkAssign()\">Assign</button>
            </div>`);
        document.body.appendChild(modal);
    }

    async bulkAssign() {
        const owner = Number(document.getElementById('proj-bulk-owner').value);
        if (!owner) return this.app.showToast('Enter user id','error');
        for (const id of this.selected) {
            await this.app.apiCall(`/projects/${id}/assign/`, { method:'POST', body: JSON.stringify({ owner }) });
        }
        document.querySelector('.fixed.inset-0')?.remove();
        this.app.showToast('Assigned','success');
        this.loadProjectsList();
    }

    openBulkTagDialog = async () => {
        if (!this.selected.size) return this.app.showToast('Nothing selected','warning');
        const modal = this.makeModal(`
            <h3 class=\"text-lg font-semibold mb-3\">Bulk Tag</h3>
            <input id=\"proj-bulk-tags\" type=\"text\" placeholder=\"Tag IDs comma-separated\" class=\"w-full border rounded px-3 py-2 mb-4\"/>
            <div class=\"flex justify-end space-x-2\">
                <button class=\"px-3 py-1 bg-gray-200 rounded\" onclick=\"this.closest('.fixed').remove()\">Cancel</button>
                <button class=\"px-3 py-1 bg-indigo-600 text-white rounded\" onclick=\"app.projects.bulkTag()\">Apply</button>
            </div>`);
        document.body.appendChild(modal);
    }

    async bulkTag() {
        const sel = document.getElementById('proj-bulk-tags');
        const tags = Array.from(sel?.selectedOptions||[]).map(o=>Number(o.value));
        for (const id of this.selected) {
            await this.app.apiCall(`/projects/${id}/`, { method:'PATCH', body: JSON.stringify({ tags }) });
        }
        document.querySelector('.fixed.inset-0')?.remove();
        this.app.showToast('Tags added','success');
        this.loadProjectsList();
    }

    makeModal(contentHTML) {
        const wrap = document.createElement('div');
        wrap.innerHTML = `
        <div class=\"fixed inset-0 z-50 flex items-center justify-center\"> 
            <div class=\"absolute inset-0 bg-black bg-opacity-40\" onclick=\"this.parentElement.remove()\"></div>
            <div class=\"relative bg-white rounded-lg shadow-lg w-full max-w-md p-5 dark:bg-slate-800\">${contentHTML}</div>
        </div>`;
        return wrap.firstElementChild;
    }

    exportProjects(){
        // build URL with filters
        let url = '/projects/export/?';
        const searchTerm = document.getElementById('project-search').value;
        const statusFilter = document.getElementById('project-status-filter').value;
        const ordering = document.getElementById('project-sort')?.value;
        if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
        if (statusFilter) url += `active=${statusFilter}&`;
        if (ordering) url += `ordering=${encodeURIComponent(ordering)}&`;
        // Auth header download
        const full = (window.CRM_CONFIG.API_BASE_URL || '').replace(/\/+$/,'') + url;
        fetch(full, { headers: { 'Authorization': `Token ${localStorage.getItem(window.CRM_CONFIG.AUTH_TOKEN_KEY) || ''}` } })
          .then(r=> r.blob())
          .then(blob => { const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='projects_export.csv'; a.click(); URL.revokeObjectURL(a.href); })
          .catch(()=> this.app.showToast('Export failed','error'));
    }

    // Actions
    async completeProject(id) {
        try {
            await this.app.apiCall(`/projects/${id}/complete/`, { method: 'POST' });
            this.app.showToast('Project completed', 'success');
            this.loadProjectsList();
        } catch(e) { this.app.showToast('Complete failed', 'error'); }
    }

    async reopenProject(id) {
        try {
            await this.app.apiCall(`/projects/${id}/reopen/`, { method: 'POST' });
            this.app.showToast('Project reopened', 'success');
            this.loadProjectsList();
        } catch(e) { this.app.showToast('Reopen failed', 'error'); }
    }

    async assignProject(id) {
        try {
            await Typeahead.open({
                title:'Assign Project', placeholder:'Search users...', multiple:false,
                fetcher: async(q)=>{ const res=await this.app.apiCall(`/users/?search=${encodeURIComponent(q||'')}`); return (res.results||res).map(u=>({id:u.id,name:u.first_name||u.username})) },
                onApply: async(ids)=>{ const owner=ids[0]; if(!owner) return; await this.app.apiCall(`/projects/${id}/assign/`, { method:'POST', body: JSON.stringify({ owner }) }); this.app.showToast('Project assigned','success'); this.loadProjectsList(); }
            });
        } catch(e) {}
        return;
    }
}

/* ===== Merged UX patches from projects-ux.js ===== */

/**
 * UX Enhancements for Projects Module
 */

if (typeof ProjectManager !== 'undefined' && window.uxEnhancements) {
    
    // Enhanced loadProjectsList
    const originalLoadProjectsList = ProjectManager.prototype.loadProjectsList;
    ProjectManager.prototype.loadProjectsList = async function(searchTerm = '') {
        const content = document.getElementById('projects-content');
        
        // Show skeleton
        window.uxEnhancements.showSkeleton(content, 'cards', 6);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const projects = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.PROJECTS}?${searchParam}`);
            
            if (!projects.results || projects.results.length === 0) {
                window.uxEnhancements.showEmptyState(content, {
                    icon: '📊',
                    title: searchTerm ? 'No projects found' : 'No projects yet',
                    description: searchTerm 
                        ? `No projects match "${searchTerm}"`
                        : 'Organize your work by creating your first project',
                    actionLabel: 'Create Project',
                    actionHandler: 'app.projects.showProjectForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("project-search").value=""; app.projects.loadProjectsList()'
                    } : null
                });
                return;
            }

            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${projects.results.map(project => this.renderProjectCard(project)).join('')}
                </div>
            `;

        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load projects',
                message: 'Unable to fetch projects from the server.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.projects.loadProjectsList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // Render project card
    ProjectManager.prototype.renderProjectCard = function(project) {
        const progress = project.progress || 0;
        const statusConfig = {
            'planning': { color: 'bg-secondary-500', label: 'Planning' },
            'active': { color: 'bg-primary-500', label: 'Active' },
            'on_hold': { color: 'bg-warning-500', label: 'On Hold' },
            'completed': { color: 'bg-success-500', label: 'Completed' },
            'cancelled': { color: 'bg-error-500', label: 'Cancelled' }
        };
        const status = statusConfig[project.status] || statusConfig.planning;

        return `
            <div class="card p-6 hover:shadow-medium transition-shadow" data-id="${project.id}">
                <div class="flex items-start justify-between mb-4">
                    <h3 class="text-lg font-semibold text-surface-900 flex-1">${project.name}</h3>
                    <span class="badge ${this.getStatusBadgeClass(project.status)}">${status.label}</span>
                </div>
                
                ${project.description ? `
                    <p class="text-sm text-surface-600 mb-4 line-clamp-2">${project.description}</p>
                ` : ''}
                
                <!-- Progress bar -->
                <div class="mb-4">
                    <div class="flex items-center justify-between text-sm mb-2">
                        <span class="text-surface-600">Progress</span>
                        <span class="font-semibold text-surface-900">${progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${status.color}" style="width: ${progress}%"></div>
                    </div>
                </div>
                
                <div class="flex items-center justify-between text-sm text-surface-600">
                    ${project.start_date ? `
                        <div class="flex items-center gap-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                            ${new Date(project.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                    ` : '<div></div>'}
                    
                    ${project.team_size ? `
                        <div class="flex items-center gap-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            ${project.team_size} members
                        </div>
                    ` : ''}
                </div>
                
                <div class="flex gap-2 mt-4 pt-4 border-t border-surface-200">
                    <button data-action="projects.viewProject" data-id="${project.id}" class="btn btn-secondary btn-sm flex-1">
                        View
                    </button>
                    <button data-action="projects.editProject" data-id="${project.id}" class="btn btn-text btn-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    };

    // Enhanced showProjectForm with unified modal
    const originalShowProjectForm = ProjectManager.prototype.showProjectForm;
    ProjectManager.prototype.showProjectForm = function(projectId = null) {
        const isEdit = projectId !== null;
        const title = isEdit ? 'Edit Project' : 'Create New Project';

        const modal = document.createElement('div');
        modal.id = 'project-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in dark:bg-slate-800 dark:text-slate-100">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('project-modal').remove(); document.body.style.overflow='';">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="project-form" class="modal-body space-y-4">
                    <div class="input-group">
                        <label for="name" class="input-label">Project Name *</label>
                        <input type="text" id="name" name="name" required class="input" placeholder="Q4 Revamp">
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="start_date" class="input-label">Start Date</label>
                            <input type="date" id="start_date" name="start_date" class="input">
                        </div>
                        <div class="input-group">
                            <label for="status" class="input-label">Status</label>
                            <select id="status" name="status" class="input select">
                                <option value="planning">Planning</option>
                                <option value="active">Active</option>
                                <option value="on_hold">On Hold</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" data-advanced="true">
                        <div class="input-group">
                            <label for="progress" class="input-label">Progress (%)</label>
                            <input type="number" id="progress" name="progress" class="input" min="0" max="100" placeholder="0">
                        </div>
                        <div class="input-group">
                            <label for="team_size" class="input-label">Team Size</label>
                            <input type="number" id="team_size" name="team_size" class="input" min="1" placeholder="1">
                        </div>
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('project-modal').remove(); document.body.style.overflow='';">
                        Cancel
                    </button>
                    <button type="submit" form="project-form" class="btn btn-primary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${isEdit ? 'Update' : 'Create'} Project
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Disable background scroll and setup close handlers
        document.body.style.overflow = 'hidden';
        const overlayEl = modal; // .modal-overlay
        const dialogEl = modal.querySelector('.modal');
        const closeModal = () => {
            overlayEl.remove();
            document.body.style.overflow = '';
            document.removeEventListener('keydown', onKeyDown);
        };
        const onKeyDown = (e) => { if (e.key === 'Escape') closeModal(); };
        document.addEventListener('keydown', onKeyDown);
        overlayEl.addEventListener('click', (e) => { if (!dialogEl.contains(e.target)) closeModal(); });
        
        const projectForm = document.getElementById('project-form');
        
        // Progressive disclosure
        if (window.advancedUX) {
            window.advancedUX.setupProgressiveDisclosure(projectForm);
        }
        
        if (isEdit && this.loadProjectData) {
            this.loadProjectData(projectId);
        }

        projectForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const formData = new FormData(projectForm);
                const projectData = Object.fromEntries(formData.entries());
                const method = projectId ? 'PUT' : 'POST';
                const url = projectId 
                    ? `${window.CRM_CONFIG.ENDPOINTS.PROJECTS}${projectId}/` 
                    : window.CRM_CONFIG.ENDPOINTS.PROJECTS;
                await window.apiClient.request(url, { method, body: JSON.stringify(projectData) });
                closeModal();
                if (this.loadProjectsList) this.loadProjectsList();
                this.app?.showToast(`Project ${projectId ? 'updated' : 'created'} successfully`, 'success');
            } catch (error) {
                // backend validation mapping
                try { window.uxEnhancements?.showFormErrors(document.getElementById('project-form'), error); } catch(_){}

                window.uxEnhancements?.showErrorModal({
                    title: `Failed to ${projectId ? 'update' : 'create'} project`,
                    message: error.message || 'Please try again',
                    error,
                    actions: [
                        { label: 'Try Again', handler: `app.projects.saveProject(${projectId})`, primary: true },
                        { label: 'Cancel', handler: '', primary: false }
                    ]
                });
            }
        });

        setTimeout(() => document.getElementById('name').focus(), 100);
    };

    // Status badge class
    ProjectManager.prototype.getStatusBadgeClass = function(status) {
        const classes = {
            'planning': 'badge-secondary',
            'active': 'badge-primary',
            'on_hold': 'badge-warning',
            'completed': 'badge-success',
            'cancelled': 'badge-error'
        };
        return classes[status] || 'badge-secondary';
    };

    // Setup search progress
    const originalLoadProjects = ProjectManager.prototype.loadProjects;
    ProjectManager.prototype.loadProjects = function() {
        originalLoadProjects.call(this);
        
        setTimeout(() => {
            const searchInput = document.getElementById('project-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadProjectsList(term);
                });
            }
        }, 100);
    };
}
