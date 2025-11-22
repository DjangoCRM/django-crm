// Frontend validation and normalization utilities
class FormValidators {
    /**
     * Normalize email to lowercase
     * @param {string} value - Email value
     * @returns {string} Normalized email
     */
    static normalizeEmail(value) {
        if (!value) return value;
        return value.trim().toLowerCase();
    }

    /**
     * Normalize phone number to +digits format (matching backend logic)
     * @param {string} value - Phone value
     * @returns {string} Normalized phone number
     */
    static normalizePhone(value) {
        if (!value) return value;
        
        // Keep leading + and digits only (matching backend _normalize_phone)
        value = value.trim();
        if (value.startsWith('+')) {
            return '+' + value.slice(1).replace(/\D/g, '');
        }
        return value.replace(/\D/g, '');
    }

    /**
     * Apply normalization to a form field
     * @param {HTMLElement} field - Form field element
     * @param {string} type - Normalization type ('email' or 'phone')
     */
    static normalizeField(field, type) {
        if (!field || !field.value) return;

        const originalValue = field.value;
        let normalizedValue;

        switch (type) {
            case 'email':
                normalizedValue = this.normalizeEmail(originalValue);
                break;
            case 'phone':
                normalizedValue = this.normalizePhone(originalValue);
                break;
            default:
                return;
        }

        if (normalizedValue !== originalValue) {
            field.value = normalizedValue;
            // Dispatch input event to trigger any listeners
            field.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    /**
     * Setup automatic normalization on form fields
     * @param {HTMLElement} form - Form element
     */
    static setupFormNormalization(form) {
        if (!form) return;

        // Email fields
        const emailFields = form.querySelectorAll('input[type="email"], input[name*="email"]');
        emailFields.forEach(field => {
            // Normalize on blur (when user leaves the field)
            field.addEventListener('blur', () => {
                this.normalizeField(field, 'email');
            });

            // Also normalize before form submission
            field.addEventListener('change', () => {
                this.normalizeField(field, 'email');
            });
        });

        // Phone fields
        const phoneFields = form.querySelectorAll('input[type="tel"], input[name*="phone"], input[name*="mobile"]');
        phoneFields.forEach(field => {
            // Normalize on blur (when user leaves the field)
            field.addEventListener('blur', () => {
                this.normalizeField(field, 'phone');
            });

            // Also normalize before form submission
            field.addEventListener('change', () => {
                this.normalizeField(field, 'phone');
            });
        });

        // Normalize all fields before form submission
        form.addEventListener('submit', (e) => {
            emailFields.forEach(field => this.normalizeField(field, 'email'));
            phoneFields.forEach(field => this.normalizeField(field, 'phone'));
        });
    }

    /**
     * Validate email format (basic client-side validation)
     * @param {string} value - Email value
     * @returns {boolean} Is valid email
     */
    static isValidEmail(value) {
        if (!value) return true; // Empty is valid (let backend handle required validation)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    }

    /**
     * Validate phone format (basic client-side validation)
     * @param {string} value - Phone value
     * @returns {boolean} Is valid phone
     */
    static isValidPhone(value) {
        if (!value) return true; // Empty is valid (let backend handle required validation)
        // After normalization, should be +digits or just digits
        const phoneRegex = /^\+?[1-9]\d{1,14}$/;
        return phoneRegex.test(value);
    }

    /**
     * Add visual validation feedback to a field
     * @param {HTMLElement} field - Form field
     * @param {boolean} isValid - Validation result
     * @param {string} message - Error message
     */
    static showValidationFeedback(field, isValid, message = '') {
        // Remove existing validation classes
        field.classList.remove('border-red-500', 'border-green-500');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }

        if (isValid) {
            field.classList.add('border-green-500');
        } else {
            field.classList.add('border-red-500');
            
            if (message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'validation-error text-red-500 text-sm mt-1';
                errorDiv.textContent = message;
                field.parentNode.appendChild(errorDiv);
            }
        }
    }

    /**
     * Setup real-time validation for form fields
     * @param {HTMLElement} form - Form element
     */
    static setupFormValidation(form) {
        if (!form) return;

        // Email fields validation
        const emailFields = form.querySelectorAll('input[type="email"], input[name*="email"]');
        emailFields.forEach(field => {
            field.addEventListener('blur', () => {
                if (field.value) {
                    const isValid = this.isValidEmail(field.value);
                    this.showValidationFeedback(field, isValid, 
                        isValid ? '' : 'Please enter a valid email address');
                }
            });

            field.addEventListener('input', () => {
                // Clear validation on input
                field.classList.remove('border-red-500', 'border-green-500');
                const existingError = field.parentNode.querySelector('.validation-error');
                if (existingError) {
                    existingError.remove();
                }
            });
        });

        // Phone fields validation
        const phoneFields = form.querySelectorAll('input[type="tel"], input[name*="phone"], input[name*="mobile"]');
        phoneFields.forEach(field => {
            field.addEventListener('blur', () => {
                if (field.value) {
                    const normalizedValue = this.normalizePhone(field.value);
                    const isValid = this.isValidPhone(normalizedValue);
                    this.showValidationFeedback(field, isValid, 
                        isValid ? '' : 'Please enter a valid phone number');
                }
            });

            field.addEventListener('input', () => {
                // Clear validation on input
                field.classList.remove('border-red-500', 'border-green-500');
                const existingError = field.parentNode.querySelector('.validation-error');
                if (existingError) {
                    existingError.remove();
                }
            });
        });
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.FormValidators = FormValidators;
}