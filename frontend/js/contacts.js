// Contact management functionality
class ContactManager {
    constructor(app) {
        this.app = app;
    }

    async loadContacts() {
        const section = document.getElementById('contacts-section');
        section.innerHTML = `
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-semibold text-gray-900">Contacts</h2>
                        <div class="flex space-x-2">
                            <input type="text" id="contact-search" placeholder="Search contacts..." 
                                   class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                            <button onclick="app.contacts.showContactForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
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
            const contacts = await this.app.apiCall(`/v1/contacts/?${searchParam}`);
            const content = document.getElementById('contacts-content');
            
            if (!contacts.results || contacts.results.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
                            👥
                        </div>
                        <p class="text-gray-500 mb-4">${searchTerm ? 'No contacts found for your search' : 'No contacts found'}</p>
                        <button onclick="app.contacts.showContactForm()" class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg">
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
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="flex-shrink-0 h-10 w-10">
                                                <div class="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-medium">
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
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${contact.disqualified ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
                                            ${contact.disqualified ? 'Disqualified' : 'Active'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div class="flex space-x-2">
                                            <button onclick="app.contacts.viewContact(${contact.id})" class="text-primary-600 hover:text-primary-900">View</button>
                                            <button onclick="app.contacts.editContact(${contact.id})" class="text-yellow-600 hover:text-yellow-900">Edit</button>
                                            <button onclick="app.contacts.deleteContact(${contact.id})" class="text-red-600 hover:text-red-900">Delete</button>
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
            document.getElementById('contacts-content').innerHTML = '<div class="text-red-600 text-center py-4">Error loading contacts</div>';
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
            <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">${title}</h3>
                        <button onclick="document.getElementById('contact-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        <div>
                            <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input type="text" id="last_name" name="last_name" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                    </div>
                    
                    <div>
                        <label for="title" class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                        <input type="text" id="title" name="title"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input type="email" id="email" name="email"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                        <div>
                            <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                            <input type="tel" id="phone" name="phone"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        </div>
                    </div>
                    
                    <div>
                        <label for="company" class="block text-sm font-medium text-gray-700 mb-1">Company</label>
                        <select id="company" name="company" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                            <option value="">Select Company</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea id="description" name="description" rows="3"
                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"></textarea>
                    </div>
                    
                    <div class="flex items-center">
                        <input type="checkbox" id="disqualified" name="disqualified"
                               class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                        <label for="disqualified" class="ml-2 block text-sm text-gray-900">Disqualified</label>
                    </div>
                    
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="document.getElementById('contact-modal').remove()" 
                                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                            Cancel
                        </button>
                        <button type="submit" class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
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
        document.getElementById('contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveContact(contactId);
        });
    }

    async loadCompaniesDropdown() {
        try {
            const companies = await this.app.apiCall('/v1/companies/');
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
            const contact = await this.app.apiCall(`/v1/contacts/${contactId}/`);
            
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
            const url = contactId ? `/v1/contacts/${contactId}/` : '/v1/contacts/';
            
            await this.app.apiCall(url, {
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
            await this.app.apiCall(`/v1/contacts/${contactId}/`, { method: 'DELETE' });
            this.loadContactsList();
            this.app.showToast('Contact deleted successfully', 'success');
        } catch (error) {
            this.app.showToast('Error deleting contact', 'error');
        }
    }

    async viewContact(contactId) {
        try {
            const contact = await this.app.apiCall(`/v1/contacts/${contactId}/`);
            
            const modal = document.createElement('div');
            modal.id = 'contact-view-modal';
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center';
            
            modal.innerHTML = `
                <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h3 class="text-lg font-medium text-gray-900">Contact Details</h3>
                            <button onclick="document.getElementById('contact-view-modal').remove()" class="text-gray-400 hover:text-gray-600">
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
                                <div class="h-20 w-20 rounded-full bg-primary-500 flex items-center justify-center text-white text-2xl font-bold">
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
                                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${contact.disqualified ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
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
                            <button onclick="app.contacts.editContact(${contact.id}); document.getElementById('contact-view-modal').remove();" 
                                    class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
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