// UI Helper Functions for Business CRM

// Password visibility toggle
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('password-toggle-icon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// Enhanced modal creation with Bitrix24-style design
function createBusinessModal(title, content, actions = [], options = {}) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4';
    
    const size = options.size || 'md';
    const sizeClasses = {
        'sm': 'max-w-md',
        'md': 'max-w-2xl',
        'lg': 'max-w-4xl',
        'xl': 'max-w-6xl'
    };
    
    modal.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl ${sizeClasses[size]} w-full max-h-[90vh] overflow-hidden">
            <!-- Header -->
            <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600 transition-colors">
                        <i class="fas fa-times text-lg"></i>
                    </button>
                </div>
            </div>
            
            <!-- Body -->
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                ${content}
            </div>
            
            <!-- Footer -->
            ${actions.length > 0 ? `
                <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                    ${actions.map(action => `
                        <button class="${action.class || 'bg-gray-500 hover:bg-gray-600 text-white'} px-4 py-2 rounded-lg font-medium transition-colors" 
                                ${action.onclick ? `onclick="${action.onclick}"` : ''}>
                            ${action.icon ? `<i class="${action.icon} mr-2"></i>` : ''}${action.text}
                        </button>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
    
    return modal;
}

// Enhanced form field creation
function createFormField(config) {
    const {
        type = 'text',
        id,
        name = id,
        label,
        placeholder = '',
        required = false,
        icon,
        options = [],
        rows = 3,
        value = ''
    } = config;
    
    let fieldHtml = '';
    
    // Label
    if (label) {
        fieldHtml += `
            <label for="${id}" class="block text-sm font-semibold text-gray-700 mb-2">
                ${icon ? `<i class="${icon} mr-2 text-gray-400"></i>` : ''}${label}${required ? ' *' : ''}
            </label>
        `;
    }
    
    // Field based on type
    switch (type) {
        case 'select':
            fieldHtml += `
                <select id="${id}" name="${name}" ${required ? 'required' : ''} 
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                    ${placeholder ? `<option value="">${placeholder}</option>` : ''}
                    ${options.map(opt => `<option value="${opt.value}" ${opt.selected ? 'selected' : ''}>${opt.text}</option>`).join('')}
                </select>
            `;
            break;
            
        case 'textarea':
            fieldHtml += `
                <textarea id="${id}" name="${name}" rows="${rows}" ${required ? 'required' : ''} 
                          placeholder="${placeholder}"
                          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-vertical">${value}</textarea>
            `;
            break;
            
        case 'checkbox':
            fieldHtml += `
                <div class="flex items-center">
                    <input type="checkbox" id="${id}" name="${name}" ${value ? 'checked' : ''} 
                           class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                    <label for="${id}" class="ml-3 text-sm text-gray-700">${label}</label>
                </div>
            `;
            break;
            
        default:
            fieldHtml += `
                <input type="${type}" id="${id}" name="${name}" ${required ? 'required' : ''} 
                       placeholder="${placeholder}" value="${value}"
                       class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
            `;
    }
    
    return `<div class="space-y-2">${fieldHtml}</div>`;
}

// Enhanced card component
function createBusinessCard(config) {
    const {
        title,
        subtitle,
        content,
        icon,
        color = 'primary',
        clickable = false,
        actions = []
    } = config;
    
    const colorClasses = {
        primary: 'bg-primary-50 text-primary-600',
        success: 'bg-success-50 text-success-600',
        warning: 'bg-warning-50 text-warning-600',
        danger: 'bg-danger-50 text-danger-600',
        gray: 'bg-gray-50 text-gray-600'
    };
    
    return `
        <div class="bg-white rounded-lg border border-gray-200 p-6 ${clickable ? 'hover:shadow-md cursor-pointer' : ''} transition-shadow">
            ${title ? `
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        ${icon ? `
                            <div class="w-10 h-10 ${colorClasses[color]} rounded-lg flex items-center justify-center">
                                <i class="${icon} text-lg"></i>
                            </div>
                        ` : ''}
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                            ${subtitle ? `<p class="text-sm text-gray-500">${subtitle}</p>` : ''}
                        </div>
                    </div>
                    ${actions.length > 0 ? `
                        <div class="flex items-center space-x-2">
                            ${actions.map(action => `
                                <button class="text-gray-400 hover:text-gray-600 transition-colors" 
                                        ${action.onclick ? `onclick="${action.onclick}"` : ''}
                                        title="${action.title || ''}">
                                    <i class="${action.icon}"></i>
                                </button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            <div>${content}</div>
        </div>
    `;
}

// Status badge component
function createStatusBadge(text, type = 'default') {
    const typeClasses = {
        success: 'bg-success-100 text-success-800',
        warning: 'bg-warning-100 text-warning-800',
        danger: 'bg-danger-100 text-danger-800',
        info: 'bg-primary-100 text-primary-800',
        default: 'bg-gray-100 text-gray-800'
    };
    
    return `<span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${typeClasses[type]}">${text}</span>`;
}

// Data table component
function createDataTable(config) {
    const { columns, data, actions = [] } = config;
    
    return `
        <div class="overflow-x-auto">
            <table class="min-w-full">
                <thead class="bg-gray-50">
                    <tr>
                        ${columns.map(col => `
                            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                ${col.label}
                            </th>
                        `).join('')}
                        ${actions.length > 0 ? '<th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>' : ''}
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${data.map(row => `
                        <tr class="hover:bg-gray-50 transition-colors">
                            ${columns.map(col => `
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    ${col.render ? col.render(row[col.field], row) : row[col.field] || '-'}
                                </td>
                            `).join('')}
                            ${actions.length > 0 ? `
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <div class="flex items-center space-x-2">
                                        ${actions.map(action => `
                                            <button class="text-${action.color || 'primary'}-600 hover:text-${action.color || 'primary'}-700 transition-colors"
                                                    onclick="${action.onclick}(${row.id})"
                                                    title="${action.title}">
                                                <i class="${action.icon}"></i>
                                            </button>
                                        `).join('')}
                                    </div>
                                </td>
                            ` : ''}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Loading state component
function createLoadingState(text = 'Loading...') {
    return `
        <div class="flex items-center justify-center py-12">
            <div class="flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                <span class="text-gray-600 font-medium">${text}</span>
            </div>
        </div>
    `;
}

// Empty state component
function createEmptyState(config) {
    const { 
        icon = 'fas fa-inbox',
        title = 'No data found',
        description = '',
        actionText = '',
        actionClick = ''
    } = config;
    
    return `
        <div class="text-center py-12">
            <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
                <i class="${icon} text-4xl"></i>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">${title}</h3>
            ${description ? `<p class="text-gray-500 mb-6">${description}</p>` : ''}
            ${actionText ? `
                <button onclick="${actionClick}" class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                    ${actionText}
                </button>
            ` : ''}
        </div>
    `;
}

// Export functions for global use
window.UIHelpers = {
    createBusinessModal,
    createFormField,
    createBusinessCard,
    createStatusBadge,
    createDataTable,
    createLoadingState,
    createEmptyState
};