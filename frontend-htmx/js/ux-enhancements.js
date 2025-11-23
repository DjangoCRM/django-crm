/**
 * UX Enhancements for Enhanced Lead Management
 * Provides modern UX patterns and interactions
 */

class UXEnhancements {
    constructor() {
        this.tooltips = new Map();
        this.observers = new Map();
        this.init();
    }

    init() {
        this.setupTooltips();
        this.setupKeyboardNavigation();
        this.setupIntersectionObserver();
        this.setupClickOutside();
        this.setupProgressiveDisclosure();
    }

    /**
     * Tooltip system
     */
    setupTooltips() {
        document.addEventListener('mouseenter', (e) => {
            if (e.target.hasAttribute('title') && e.target.title) {
                this.showTooltip(e.target, e.target.title);
                e.target.setAttribute('data-tooltip', e.target.title);
                e.target.removeAttribute('title');
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                this.hideTooltip(e.target);
            }
        }, true);
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip show';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;

        this.tooltips.set(element, tooltip);

        // Auto-hide after 5 seconds
        setTimeout(() => this.hideTooltip(element), 5000);
    }

    hideTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.remove();
            this.tooltips.delete(element);
        }
    }

    /**
     * Enhanced keyboard navigation
     */
    setupKeyboardNavigation() {
        let focusableElements = [];
        let currentIndex = -1;

        // Tab navigation for cards
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                focusableElements = Array.from(document.querySelectorAll(
                    '.lead-card, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
                )).filter(el => {
                    return el.offsetParent !== null && !el.disabled;
                });
            }

            // Arrow key navigation in grid
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                const activeCard = document.activeElement.closest('.lead-card');
                if (activeCard) {
                    e.preventDefault();
                    this.navigateCards(e.key, activeCard);
                }
            }

            // Enter to select/activate
            if (e.key === 'Enter') {
                const activeCard = document.activeElement.closest('.lead-card');
                if (activeCard) {
                    const leadId = activeCard.getAttribute('data-lead-id');
                    if (leadId) {
                        app.leads.viewLead(parseInt(leadId));
                    }
                }
            }

            // Space to select checkbox
            if (e.key === ' ') {
                const activeCard = document.activeElement.closest('.lead-card');
                if (activeCard) {
                    e.preventDefault();
                    const checkbox = activeCard.querySelector('.lead-checkbox');
                    if (checkbox) {
                        checkbox.click();
                    }
                }
            }
        });
    }

    navigateCards(direction, currentCard) {
        const cards = Array.from(document.querySelectorAll('.lead-card'));
        const currentIndex = cards.indexOf(currentCard);
        const columns = this.getGridColumns();
        
        let nextIndex;
        
        switch (direction) {
            case 'ArrowLeft':
                nextIndex = currentIndex - 1;
                break;
            case 'ArrowRight':
                nextIndex = currentIndex + 1;
                break;
            case 'ArrowUp':
                nextIndex = currentIndex - columns;
                break;
            case 'ArrowDown':
                nextIndex = currentIndex + columns;
                break;
        }
        
        if (nextIndex >= 0 && nextIndex < cards.length) {
            cards[nextIndex].focus();
        }
    }

    getGridColumns() {
        const container = document.querySelector('.grid');
        if (!container) return 1;
        
        const computedStyle = getComputedStyle(container);
        const gridTemplateColumns = computedStyle.gridTemplateColumns;
        return gridTemplateColumns.split(' ').length;
    }

    /**
     * Intersection Observer for infinite scroll and animations
     */
    setupIntersectionObserver() {
        // Animate cards on scroll
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Observe new cards
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 && node.classList.contains('lead-card')) {
                        node.style.opacity = '0';
                        node.style.transform = 'translateY(20px)';
                        node.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                        cardObserver.observe(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        this.observers.set('cards', cardObserver);
        this.observers.set('mutations', observer);
    }

    /**
     * Click outside to close
     */
    setupClickOutside() {
        document.addEventListener('click', (e) => {
            // Close dropdowns
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }

            // Close modals on backdrop click
            if (e.target.classList.contains('modal-overlay')) {
                e.target.remove();
                document.body.style.overflow = '';
            }
        });
    }

    /**
     * Progressive disclosure
     */
    setupProgressiveDisclosure() {
        // Auto-expand sections based on content
        document.addEventListener('input', (e) => {
            if (e.target.type === 'text' || e.target.type === 'email') {
                const section = e.target.closest('.form-section');
                if (section && e.target.value.length > 0) {
                    this.expandFormSection(section);
                }
            }
        });
    }

    expandFormSection(section) {
        const hiddenFields = section.querySelectorAll('.form-group.hidden');
        hiddenFields.forEach((field, index) => {
            setTimeout(() => {
                field.classList.remove('hidden');
                field.style.opacity = '0';
                field.style.transform = 'translateY(-10px)';
                field.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                
                setTimeout(() => {
                    field.style.opacity = '1';
                    field.style.transform = 'translateY(0)';
                }, 50);
            }, index * 100);
        });
    }

    /**
     * Smart defaults and auto-completion
     */
    applySmartDefaults(form, leadData = {}) {
        // Email domain suggestions
        const emailInput = form.querySelector('input[type="email"]');
        if (emailInput) {
            this.setupEmailSuggestions(emailInput);
        }

        // Phone formatting
        const phoneInputs = form.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            this.setupPhoneFormatting(input);
        });

        // Company name autocomplete
        const companyInput = form.querySelector('input[name="company_name"]');
        if (companyInput) {
            this.setupCompanyAutocomplete(companyInput);
        }

        // Auto-populate from existing data
        if (leadData.email && leadData.email.includes('@')) {
            const domain = leadData.email.split('@')[1];
            this.suggestCompanyFromEmail(form, domain);
        }
    }

    setupEmailSuggestions(input) {
        const commonDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'];
        
        input.addEventListener('input', (e) => {
            const value = e.target.value;
            const atIndex = value.lastIndexOf('@');
            
            if (atIndex > 0 && atIndex < value.length - 1) {
                const domain = value.substring(atIndex + 1);
                const suggestions = commonDomains.filter(d => d.startsWith(domain));
                
                if (suggestions.length > 0) {
                    this.showEmailSuggestions(input, value.substring(0, atIndex + 1), suggestions);
                }
            }
        });
    }

    showEmailSuggestions(input, prefix, domains) {
        // Remove existing suggestions
        const existing = document.querySelector('.email-suggestions');
        if (existing) existing.remove();

        const suggestions = document.createElement('div');
        suggestions.className = 'email-suggestions absolute z-50 mt-1 bg-white border border-gray-300 rounded-md shadow-lg';
        suggestions.style.width = input.offsetWidth + 'px';
        
        domains.slice(0, 3).forEach(domain => {
            const suggestion = document.createElement('div');
            suggestion.className = 'px-3 py-2 hover:bg-blue-50 cursor-pointer text-sm';
            suggestion.textContent = prefix + domain;
            suggestion.onclick = () => {
                input.value = prefix + domain;
                suggestions.remove();
                input.focus();
            };
            suggestions.appendChild(suggestion);
        });

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(suggestions);

        // Remove on click outside
        setTimeout(() => {
            document.addEventListener('click', function removeSuggestions(e) {
                if (!suggestions.contains(e.target) && e.target !== input) {
                    suggestions.remove();
                    document.removeEventListener('click', removeSuggestions);
                }
            });
        }, 100);
    }

    setupPhoneFormatting(input) {
        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = `(${value}`;
                } else if (value.length <= 6) {
                    value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
                } else {
                    value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
                }
            }
            
            e.target.value = value;
        });
    }

    setupCompanyAutocomplete(input) {
        let timeout;
        
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const query = e.target.value;
            
            if (query.length > 2) {
                timeout = setTimeout(async () => {
                    try {
                        const suggestions = await this.getCompanySuggestions(query);
                        this.showCompanySuggestions(input, suggestions);
                    } catch (error) {
                        console.error('Company suggestions error:', error);
                    }
                }, 300);
            }
        });
    }

    async getCompanySuggestions(query) {
        // This could integrate with external APIs like Clearbit, FullContact, etc.
        // For now, we'll use internal company data
        try {
            const response = await window.apiClient.get(`companies/?search=${encodeURIComponent(query)}&limit=5`);
            return response.results || [];
        } catch (error) {
            return [];
        }
    }

    showCompanySuggestions(input, companies) {
        const existing = document.querySelector('.company-suggestions');
        if (existing) existing.remove();

        if (companies.length === 0) return;

        const suggestions = document.createElement('div');
        suggestions.className = 'company-suggestions absolute z-50 mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto';
        suggestions.style.width = input.offsetWidth + 'px';
        
        companies.forEach(company => {
            const suggestion = document.createElement('div');
            suggestion.className = 'px-3 py-2 hover:bg-blue-50 cursor-pointer';
            suggestion.innerHTML = `
                <div class="font-medium text-sm">${company.full_name}</div>
                ${company.website ? `<div class="text-xs text-gray-500">${company.website}</div>` : ''}
            `;
            suggestion.onclick = () => {
                input.value = company.full_name;
                
                // Auto-fill related fields if available
                const form = input.closest('form');
                if (company.website) {
                    const websiteInput = form.querySelector('input[name="website"]');
                    if (websiteInput && !websiteInput.value) {
                        websiteInput.value = company.website;
                    }
                }
                
                suggestions.remove();
                input.focus();
            };
            suggestions.appendChild(suggestion);
        });

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(suggestions);
    }

    suggestCompanyFromEmail(form, domain) {
        // Common email domain to company mappings
        const domainCompanyMap = {
            'google.com': 'Google',
            'microsoft.com': 'Microsoft',
            'apple.com': 'Apple',
            'amazon.com': 'Amazon',
            'facebook.com': 'Meta',
            'tesla.com': 'Tesla',
            'netflix.com': 'Netflix'
        };

        const companyInput = form.querySelector('input[name="company_name"]');
        if (companyInput && !companyInput.value && domainCompanyMap[domain]) {
            companyInput.value = domainCompanyMap[domain];
            
            // Add a subtle highlight to show it was auto-filled
            companyInput.style.backgroundColor = '#fef3cd';
            setTimeout(() => {
                companyInput.style.backgroundColor = '';
            }, 2000);
        }
    }

    /**
     * Advanced form validation with real-time feedback
     */
    setupAdvancedValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Real-time validation
            input.addEventListener('blur', () => {
                this.validateField(input);
            });

            // Clear errors on focus
            input.addEventListener('focus', () => {
                this.clearFieldError(input);
            });
        });

        // Form submission validation
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            let isValid = true;
            inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });

            if (isValid) {
                // Process form submission
                return true;
            } else {
                // Focus first invalid field
                const firstError = form.querySelector('.form-input.error');
                if (firstError) {
                    firstError.focus();
                }
                return false;
            }
        });
    }

    validateField(input) {
        const value = input.value.trim();
        const rules = this.getValidationRules(input);
        
        for (const rule of rules) {
            if (!rule.test(value)) {
                this.showFieldError(input, rule.message);
                return false;
            }
        }

        this.clearFieldError(input);
        return true;
    }

    getValidationRules(input) {
        const rules = [];
        const name = input.name;
        const type = input.type;

        // Required fields
        if (input.hasAttribute('required')) {
            rules.push({
                test: (value) => value.length > 0,
                message: 'This field is required'
            });
        }

        // Email validation
        if (type === 'email') {
            rules.push({
                test: (value) => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
                message: 'Please enter a valid email address'
            });
        }

        // Phone validation
        if (type === 'tel') {
            rules.push({
                test: (value) => !value || /^[\d\s\-\(\)\.x\+]+$/.test(value),
                message: 'Please enter a valid phone number'
            });
        }

        // URL validation
        if (type === 'url') {
            rules.push({
                test: (value) => !value || /^https?:\/\/.+/.test(value),
                message: 'Please enter a valid URL starting with http:// or https://'
            });
        }

        return rules;
    }

    showFieldError(input, message) {
        input.classList.add('error');
        
        // Remove existing error
        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error
        const error = document.createElement('div');
        error.className = 'form-error';
        error.textContent = message;
        input.parentNode.appendChild(error);
    }

    clearFieldError(input) {
        input.classList.remove('error');
        const error = input.parentNode.querySelector('.form-error');
        if (error) {
            error.remove();
        }
    }

    /**
     * Cleanup resources
     */
    destroy() {
        this.tooltips.forEach(tooltip => tooltip.remove());
        this.tooltips.clear();
        
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

// Initialize UX enhancements
window.uxEnhancements = new UXEnhancements();
