// Contact management functionality
class ContactManager {
    constructor(app) {
        this.app = app;
    }

    async loadContacts() {
        const section = document.getElementById('contacts-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow dark:bg-slate-800">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Contacts</h2>
                        <div class="flex space-x-2">
                            <input type="text" id="contact-search" placeholder="Search contacts..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                            <button data-action="contacts.showContactForm" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                                Add Contact
                            </button>
                        </div>
                    </div>
                </div>
                <div id="contacts-content" class="p-6">
                    <div class="htmx-indicator">Loading contacts...</div>
                </div>
            </div>
        `;

        // Add search functionality
        document.getElementById('contact-search').addEventListener('input', (e) => {
            this.searchContacts(e.target.value);
        });
        
        if (this.app.token) {
            this.loadContactsList();
        }
    }

    async loadContactsList(searchTerm = '') {
        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const contacts = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}?${searchParam}`);
            const content = document.getElementById('contacts-content');
            
            if (!contacts.results || contacts.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            👥
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm ? 'No contacts found for your search' : 'No contacts found'}</p>
                        <button data-action="contacts.showContactForm" class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg">
                            Add Your First Contact
                        </button>
                    </div>
                `;
                return;
            }

            content.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${contacts.results.map(contact => `
                                <tr class=\"hover:bg-gray-50 dark:hover:bg-slate-700\">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white font-medium">
                                                    ${this.getInitials(contact.first_name, contact.last_name)}
                                                </div>
                                            </div>
                                            <div class="ml-4">
                                                <div class="text-sm font-medium text-gray-900">${contact.full_name}</div>
                                                <div class="text-sm text-gray-500">${contact.title || ''}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.company_name || 'No company'}</div>
                                        <div class="text-sm text-gray-500">${contact.city_name || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.email || 'No email'}</div>
                                        <div class="text-sm text-gray-500">${contact.secondary_email || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.phone || 'No phone'}</div>
                                        <div class="text-sm text-gray-500">${contact.mobile || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${contact.disqualified ? 'bg-danger bg-opacity-20 text-danger' : 'bg-success bg-opacity-20 text-success'}">
                                            ${contact.disqualified ? 'Disqualified' : 'Active'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button data-action="contacts.viewContact" data-id="${contact.id}" class="text-primary hover:text-primary-900">View</button>
                                            <button data-action="contacts.editContact" data-id="${contact.id}" class="text-warning hover:text-yellow-900">Edit</button>
                                            <button data-action="contacts.deleteContact" data-id="${contact.id}" class="text-danger hover:text-red-900">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                ${contacts.count > contacts.results.length ? `
                    <div class="mt-4 flex items-center justify-between">
                        <div class="text-sm text-gray-500">
                            Showing ${contacts.results.length} of ${contacts.count} contacts
                        </div>
                        <div class="flex space-x-2">
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Previous</button>
                            <button class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;
        } catch (error) {
            document.getElementById('contacts-content').innerHTML = '<div class="text-danger text-center py-4">Error loading contacts</div>';
        }
    }

    getInitials(firstName, lastName) {
        return `${(firstName || '').charAt(0)}${(lastName || '').charAt(0)}`.toUpperCase();
    }

    searchContacts(term) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadContactsList(term);
        }, 300);
    }

    showContactForm(contactId = null) {
        const isEdit = contactId !== null;
        const title = isEdit ? 'Edit Contact' : 'Add New Contact';

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'contact-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto dark:bg-slate-800">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button data-action="contact.closeContactForm" class="text-gray-400 hover:text-gray-600">
                            <span class="sr-only">Close</span>
                            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="contact-form" class="p-6 space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                            <input type="text" id="first_name" name="first_name" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                        <div>
                            <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input type="text" id="last_name" name="last_name" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                    </div>
                    
                    <div>
                        <label for="title" class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                        <input type="text" id="title" name="title"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input type="email" id="email" name="email"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                        <div>
                            <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                            <input type="tel" id="phone" name="phone"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                        </div>
                    </div>
                    
                    <div>
                        <label for="company" class="block text-sm font-medium text-gray-700 mb-1">Company</label>
                        <select id="company" name="company" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary">
                            <option value="">Select Company</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea id="description" name="description" rows="3"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"></textarea>
                    </div>
                    
                    <div class="flex items-center">
                        <input type="checkbox" id="disqualified" name="disqualified"
                               class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded">
                        <label for="disqualified" class="ml-2 block text-sm text-gray-900">Disqualified</label>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" data-action="contact.cancelContactForm" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90">
                            ${isEdit ? 'Update' : 'Create'} Contact
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Load companies for dropdown
        this.loadCompaniesDropdown();

        // If editing, load contact data
        if (isEdit) {
            this.loadContactData(contactId);
        }

        // Setup form submission
        const contactForm = document.getElementById('contact-form');
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveContact(contactId);
        });

        // Setup form normalization and validation
        if (window.FormValidators) {
            window.FormValidators.setupFormNormalization(contactForm);
            window.FormValidators.setupFormValidation(contactForm);
        }
    }

    async loadCompaniesDropdown() {
        try {
            const companies = await window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.COMPANIES);
            const companySelect = document.getElementById('company');
            
            if (companies.results) {
                companies.results.forEach(company => {
                    const option = document.createElement('option');
                    option.value = company.id;
                    option.textContent = company.full_name;
                    companySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading companies:', error);
        }
    }

    async loadContactData(contactId) {
        try {
            const contact = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/`);
            
            // Fill form fields
            const fields = ['first_name', 'last_name', 'title', 'email', 'phone', 'description'];
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && contact[field]) {
                    element.value = contact[field];
                }
            });

            // Set company if exists
            if (contact.company) {
                document.getElementById('company').value = contact.company;
            }

            // Set disqualified checkbox
            document.getElementById('disqualified').checked = contact.disqualified;

        } catch (error) {
            this.app.showToast('Error loading contact data', 'error');
        }
    }

    async saveContact(contactId = null) {
        const formData = new FormData(document.getElementById('contact-form'));
        const contactData = Object.fromEntries(formData.entries());
        
        // Convert checkbox to boolean
        contactData.disqualified = document.getElementById('disqualified').checked;
        
        // Remove empty company field
        if (!contactData.company) {
            delete contactData.company;
        }

        try {
            const method = contactId ? 'PUT' : 'POST';
            const url = contactId ? `${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/` : window.CRM_CONFIG.ENDPOINTS.CONTACTS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(contactData)
            });

            document.getElementById('contact-modal').remove();
            this.loadContactsList();
            this.app.showToast(`Contact ${contactId ? 'updated' : 'created'} successfully`, 'success');
        } catch (error) {
            this.app.showToast(`Error ${contactId ? 'updating' : 'creating'} contact`, 'error');
        }
    }

    async editContact(contactId) {
        this.showContactForm(contactId);
    }

    async deleteContact(contactId) {
        if (!confirm('Are you sure you want to delete this contact?')) {
            return;
        }

        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/`);
            this.loadContactsList();
            this.app.showToast('Contact deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting contact', 'error');
        }
    }

    async viewContact(contactId) {
        try {
            const contact = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'contact-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 dark:bg-slate-800">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Contact Details</h3>
                            <button data-action="contact.closeViewContactModal" class="text-gray-400 hover:text-gray-600">
                                <span class="sr-only">Close</span>
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div class="p-6">
                        <div class="flex items-start space-x-6">
                            <div class="flex-shrink-0">
                                <div class="h-20 w-20 rounded-full bg-primary flex items-center justify-center text-white text-2xl font-bold">
                                    ${this.getInitials(contact.first_name, contact.last_name)}
                                </div>
                            </div>
                            
                            <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <h4 class="text-lg font-medium text-gray-900">${contact.full_name}</h4>
                                    <p class="text-gray-600">${contact.title || 'No title'}</p>
                                    
                                    <dl class="mt-4 space-y-2">
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Email</dt>
                                            <dd class="text-sm text-gray-900">${contact.email || 'No email'}</dd>
                                        </div>
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Phone</dt>
                                            <dd class="text-sm text-gray-900">${contact.phone || 'No phone'}</dd>
                                        </div>
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Company</dt>
                                            <dd class="text-sm text-gray-900">${contact.company_name || 'No company'}</dd>
                                        </div>
                                    </dl>
                                </div>
                                
                                <div>
                                    <dl class="space-y-2">
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Status</dt>
                                            <dd class="text-sm">
                                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${contact.disqualified ? 'bg-danger bg-opacity-20 text-danger' : 'bg-success bg-opacity-20 text-success'}">
                                                    ${contact.disqualified ? 'Disqualified' : 'Active'}
                                                </span>
                                            </dd>
                                        </div>
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Created</dt>
                                            <dd class="text-sm text-gray-900">${new Date(contact.creation_date).toLocaleDateString()}</dd>
                                        </div>
                                        <div>
                                            <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                                            <dd class="text-sm text-gray-900">${new Date(contact.update_date).toLocaleDateString()}</dd>
                                        </div>
                                    </dl>
                                </div>
                            </div>
                        </div>
                        
                        ${contact.description ? `
                            <div class="mt-6">
                                <h5 class="text-sm font-medium text-gray-500">Description</h5>
                                <p class="mt-1 text-sm text-gray-900">${contact.description}</p>
                            </div>
                        ` : ''}
                        
                        <div class="mt-6 flex justify-end space-x-3">
                            <button data-action="contacts.editContact" data-id="${contact.id}" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-opacity-90">
                                Edit Contact
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        } catch (error) {
            this.app.showToast('Error loading contact details', 'error');
        }
    }
}
/* ===== Merged UX patches from contacts-ux.js ===== */

/**
 * UX Enhancements for Contacts Module
 * Extends ContactManager with improved UX features
 */

// Patch ContactManager to use UX enhancements
if (typeof ContactManager !== 'undefined' && window.uxEnhancements) {
    const originalLoadContactsList = ContactManager.prototype.loadContactsList;
    const originalShowContactForm = ContactManager.prototype.showContactForm;
    const originalSaveContact = ContactManager.prototype.saveContact;
    const originalDeleteContact = ContactManager.prototype.deleteContact;

    // 1. Enhance loadContactsList with skeleton loading and empty states
    ContactManager.prototype.loadContactsList = async function(searchTerm = '') {
        const content = document.getElementById('contacts-content');
        
        // Show skeleton loading
        window.uxEnhancements.showSkeleton(content, 'list', 8);

        try {
            const searchParam = searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : '';
            const contacts = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}?${searchParam}`);
            
            if (!contacts.results || contacts.results.length === 0) {
                // Show enhanced empty state
                window.uxEnhancements.showEmptyState(content, {
                    icon: '👥',
                    title: searchTerm ? 'No contacts found' : 'No contacts yet',
                    description: searchTerm 
                        ? `We couldn't find any contacts matching "${searchTerm}"`
                        : 'Start building your network by adding your first contact',
                    actionLabel: 'Add Contact',
                    actionHandler: 'app.contacts.showContactForm()',
                    secondaryAction: searchTerm ? {
                        label: 'Clear Search',
                        handler: 'document.getElementById("contact-search").value=""; app.contacts.loadContactsList()'
                    } : null
                });
                return;
            }

            // Render contacts list
            content.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 table-responsive">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${contacts.results.map(contact => `
                                <tr class=\"hover:bg-gray-50 dark:hover:bg-slate-700\" data-id=\"${contact.id}\">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white font-medium">
                                                    ${this.getInitials(contact.first_name, contact.last_name)}
                                                </div>
                                            </div>
                                            <div class="ml-4">
                                                <div class="text-sm font-medium text-gray-900">${contact.full_name}</div>
                                                <div class="text-sm text-gray-500">${contact.title || ''}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.company_name || 'No company'}</div>
                                        <div class="text-sm text-gray-500">${contact.city_name || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.email || 'No email'}</div>
                                        <div class="text-sm text-gray-500">${contact.secondary_email || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm text-gray-900">${contact.phone || 'No phone'}</div>
                                        <div class="text-sm text-gray-500">${contact.mobile || ''}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="badge ${contact.disqualified ? 'badge-error' : 'badge-success'}">
                                            ${contact.disqualified ? 'Disqualified' : 'Active'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button data-action="contacts.viewContact" data-id="${contact.id}" class="btn btn-text btn-sm">View</button>
                                            <button data-action="contacts.editContact" data-id="${contact.id}" class="btn btn-text btn-sm">Edit</button>
                                            <button data-action="contacts.deleteContact" data-id="${contact.id}" class="btn btn-text btn-sm text-error-600">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <!-- Mobile Card View -->
                <div class="card-view">
                    ${contacts.results.map(contact => `
                        <div class="card-view-item" data-id="${contact.id}">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="avatar avatar-md bg-primary-100">
                                    <span class="text-primary-600">${this.getInitials(contact.first_name, contact.last_name)}</span>
                                </div>
                                <div class="flex-1">
                                    <h4 class="font-semibold">${contact.full_name}</h4>
                                    <p class="text-sm text-surface-600">${contact.title || ''}</p>
                                </div>
                                <span class="badge badge-sm ${contact.disqualified ? 'badge-error' : 'badge-success'}">
                                    ${contact.disqualified ? 'Disqualified' : 'Active'}
                                </span>
                            </div>
                            <div class="space-y-2">
                                ${contact.company_name ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Company</span>
                                        <span class="card-view-value">${contact.company_name}</span>
                                    </div>
                                ` : ''}
                                ${contact.email ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Email</span>
                                        <span class="card-view-value">${contact.email}</span>
                                    </div>
                                ` : ''}
                                ${contact.phone ? `
                                    <div class="card-view-row">
                                        <span class="card-view-label">Phone</span>
                                        <span class="card-view-value">${contact.phone}</span>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="flex gap-2 mt-4 pt-4 border-t border-surface-200">
                                <button data-action="contacts.viewContact" data-id="${contact.id}" class="btn btn-secondary btn-sm flex-1">View</button>
                                <button data-action="contacts.editContact" data-id="${contact.id}" class="btn btn-secondary btn-sm flex-1">Edit</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${contacts.count > contacts.results.length ? `
                    <div class="mt-6 flex items-center justify-between">
                        <div class="text-sm text-surface-600">
                            Showing ${contacts.results.length} of ${contacts.count} contacts
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-secondary btn-sm">Previous</button>
                            <button class="btn btn-secondary btn-sm">Next</button>
                        </div>
                    </div>
                ` : ''}
            `;
        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: 'Failed to load contacts',
                message: 'Unable to fetch contacts from the server. Please try again.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: 'app.contacts.loadContactsList()', primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // 2. Enhance showContactForm with smart defaults
    ContactManager.prototype.showContactForm = function(contactId = null) {
        const isEdit = contactId !== null;
        const title = isEdit ? 'Edit Contact' : 'Add New Contact';

        const modal = document.createElement('div');
        modal.id = 'contact-modal';
        modal.className = 'modal-overlay fade-in';
        
        modal.innerHTML = `
            <div class="modal w-full max-w-2xl scale-in">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="btn-icon btn-text" onclick="document.getElementById('contact-modal').remove()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="contact-form" class="modal-body space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="first_name" class="input-label">First Name *</label>
                            <input type="text" id="first_name" name="first_name" required class="input">
                        </div>
                        <div class="input-group">
                            <label for="last_name" class="input-label">Last Name *</label>
                            <input type="text" id="last_name" name="last_name" required class="input">
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="title" class="input-label">Title</label>
                        <input type="text" id="title" name="title" class="input" placeholder="e.g., Sales Manager">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="input-group">
                            <label for="email" class="input-label">Email</label>
                            <input type="email" id="email" name="email" class="input" placeholder="email@example.com">
                            <p class="input-hint">Will be converted to lowercase</p>
                        </div>
                        <div class="input-group">
                            <label for="phone" class="input-label">Phone</label>
                            <input type="tel" id="phone" name="phone" class="input" placeholder="+1234567890">
                            <p class="input-hint">Will be cleaned to +digits format</p>
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label for="company" class="input-label">Company</label>
                        <select id="company" name="company" class="input select">
                            <option value="">Select Company</option>
                        </select>
                    </div>
                    
                    <div class="input-group">
                        <label for="description" class="input-label">Description</label>
                        <textarea id="description" name="description" rows="3" class="input"></textarea>
                    </div>
                    
                    <div class="flex items-center gap-2">
                        <input type="checkbox" id="disqualified" name="disqualified" class="checkbox">
                        <label for="disqualified" class="text-sm">Mark as disqualified</label>
                    </div>
                </form>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('contact-modal').remove()">
                        Cancel
                    </button>
                    <button type="submit" form="contact-form" class="btn btn-primary">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${isEdit ? 'Update' : 'Create'} Contact
                        ${!isEdit ? '<kbd class="ml-2">⌘S</kbd>' : ''}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Load companies for dropdown
        this.loadCompaniesDropdown();

        const contactForm = document.getElementById('contact-form');

        // Apply smart defaults for new contacts
        if (!isEdit) {
            const defaults = window.uxEnhancements.getSmartDefaults('contact', this.app.user?.id);
            window.uxEnhancements.applySmartDefaults(contactForm, defaults);
        }

        // If editing, load contact data
        if (isEdit) {
            this.loadContactData(contactId);
        }

        // Setup form submission
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveContact(contactId);
        });

        // Setup form normalization and validation
        if (window.FormValidators) {
            window.FormValidators.setupFormNormalization(contactForm);
            window.FormValidators.setupFormValidation(contactForm);
        }

        // Focus first input
        setTimeout(() => document.getElementById('first_name').focus(), 100);
    };

    // 3. Enhance saveContact with optimistic updates
    ContactManager.prototype.saveContact = async function(contactId = null) {
        const formData = new FormData(document.getElementById('contact-form'));
        const contactData = Object.fromEntries(formData.entries());
        
        // Remember commonly used values
        if (contactData.company) {
            window.uxEnhancements.rememberValue('company', contactData.company);
        }
        
        contactData.disqualified = document.getElementById('disqualified').checked;
        
        if (!contactData.company) {
            delete contactData.company;
        }

        try {
            const method = contactId ? 'PUT' : 'POST';
            const url = contactId 
                ? `${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/` 
                : window.CRM_CONFIG.ENDPOINTS.CONTACTS;
            
            await window.apiClient.request(url, {
                method: method,
                body: JSON.stringify(contactData)
            });

            document.getElementById('contact-modal').remove();
            this.loadContactsList();
            this.app.showToast(
                `Contact ${contactId ? 'updated' : 'created'} successfully`, 
                'success'
            );
        } catch (error) {
            window.uxEnhancements.showErrorModal({
                title: `Failed to ${contactId ? 'update' : 'create'} contact`,
                message: error.message || 'Please check your input and try again.',
                error: error,
                actions: [
                    { label: 'Try Again', handler: `app.contacts.saveContact(${contactId})`, primary: true },
                    { label: 'Cancel', handler: '', primary: false }
                ]
            });
        }
    };

    // 4. Enhance deleteContact with undo functionality
    ContactManager.prototype.deleteContact = async function(contactId) {
        if (!confirm('Are you sure you want to delete this contact?')) {
            return;
        }

        try {
            // Get contact data before deletion for undo
            const contact = await window.apiClient.get(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/`);
            
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.CONTACTS}${contactId}/`);
            
            this.loadContactsList();
            
            // Show toast with undo option
            const toastContainer = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast toast-success toast-with-action fade-in pointer-events-auto';
            toast.innerHTML = `
                <div class="flex items-center gap-3">
                    <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <span>Contact deleted successfully</span>
                </div>
                <button class="toast-action-button" onclick="app.contacts.undoDeleteContact(${contactId}, '${JSON.stringify(contact).replace(/'/g, "\\'")}')">
                    Undo
                </button>
            `;
            
            toastContainer.appendChild(toast);
            
            // Auto-remove after 8 seconds
            setTimeout(() => toast.remove(), 8000);
            
        } catch (error) {
            this.app.showToast('Error deleting contact', 'error');
        }
    };

    // Add undo delete functionality
    ContactManager.prototype.undoDeleteContact = async function(contactId, contactDataStr) {
        try {
            const contactData = JSON.parse(contactDataStr);
            
            // Recreate contact
            await window.apiClient.post(window.CRM_CONFIG.ENDPOINTS.CONTACTS, contactData);
            
            this.loadContactsList();
            this.app.showToast('Contact restored successfully', 'success');
        } catch (error) {
            this.app.showToast('Error restoring contact', 'error');
        }
    };

    // 5. Setup search progress indicator
    const originalLoadContacts = ContactManager.prototype.loadContacts;
    ContactManager.prototype.loadContacts = function() {
        originalLoadContacts.call(this);
        
        // Setup search progress
        setTimeout(() => {
            const searchInput = document.getElementById('contact-search');
            if (searchInput && window.uxEnhancements) {
                window.uxEnhancements.setupSearchProgress(searchInput, (term) => {
                    this.loadContactsList(term);
                });
            }
        }, 100);
    };
}
