"""
Custom validation helpers for Django CRM API
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def validate_phone_number(value):
    """Validate phone number format"""
    if not value:
        return value
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', value)
    
    # Check if it's a valid format
    phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    if not phone_pattern.match(cleaned):
        raise serializers.ValidationError(
            _('Phone number must be in valid international format (e.g., +1234567890)')
        )
    
    return cleaned


def validate_email_format(value):
    """Enhanced email validation"""
    if not value:
        return value
    
    email_validator = EmailValidator()
    try:
        email_validator(value)
    except ValidationError:
        raise serializers.ValidationError(_('Enter a valid email address'))
    
    # Check for common typos
    common_domains = {
        'gmail.co': 'gmail.com',
        'yahoo.co': 'yahoo.com',
        'hotmail.co': 'hotmail.com',
        'outlook.co': 'outlook.com'
    }
    
    domain = value.split('@')[-1].lower() if '@' in value else ''
    if domain in common_domains:
        suggested = value.replace(domain, common_domains[domain])
        raise serializers.ValidationError(
            _('Did you mean "{suggested}"?').format(suggested=suggested)
        )
    
    return value.lower()


def validate_website_url(value):
    """Validate website URL"""
    if not value:
        return value
    
    # Add protocol if missing
    if not value.startswith(('http://', 'https://')):
        value = 'https://' + value
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(value):
        raise serializers.ValidationError(_('Enter a valid website URL'))
    
    return value


def validate_name_field(value, field_name="Name"):
    """Validate name fields (first_name, last_name, company name, etc.)"""
    if not value:
        return value
    
    # Remove extra whitespace
    value = value.strip()
    
    # Check minimum length
    if len(value) < 2:
        raise serializers.ValidationError(
            _(f'{field_name} must be at least 2 characters long')
        )
    
    # Check for invalid characters (only allow letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", value):
        raise serializers.ValidationError(
            _(f'{field_name} contains invalid characters')
        )
    
    # Capitalize properly
    return ' '.join(word.capitalize() for word in value.split())


def validate_currency_amount(value):
    """Validate currency amounts"""
    if value is None:
        return value
    
    if value < 0:
        raise serializers.ValidationError(_('Amount cannot be negative'))
    
    if value > 999999999.99:  # 999 million
        raise serializers.ValidationError(_('Amount is too large'))
    
    return value


def validate_probability(value):
    """Validate probability percentage (0-100)"""
    if value is None:
        return value
    
    if not 0 <= value <= 100:
        raise serializers.ValidationError(
            _('Probability must be between 0 and 100 percent')
        )
    
    return value


def validate_date_range(start_date, end_date, field_names=('start_date', 'end_date')):
    """Validate that start date is before end date"""
    if start_date and end_date and start_date > end_date:
        raise serializers.ValidationError({
            field_names[1]: _('End date must be after start date')
        })


def validate_required_fields(data, required_fields):
    """Validate that required fields are present and not empty"""
    errors = {}
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = _('This field is required')
    
    if errors:
        raise serializers.ValidationError(errors)


def validate_unique_email(email, model_class, instance=None):
    """Validate email uniqueness within a model"""
    if not email:
        return
    
    queryset = model_class.objects.filter(email__iexact=email)
    if instance:
        queryset = queryset.exclude(pk=instance.pk)
    
    if queryset.exists():
        raise serializers.ValidationError(
            _('A record with this email already exists')
        )


def validate_business_hours(time_value):
    """Validate business hours (9 AM to 6 PM)"""
    if not time_value:
        return time_value
    
    hour = time_value.hour
    if not 9 <= hour <= 18:
        raise serializers.ValidationError(
            _('Time must be during business hours (9 AM - 6 PM)')
        )
    
    return time_value


def validate_future_date(date_value, field_name="Date"):
    """Validate that date is in the future"""
    if not date_value:
        return date_value
    
    from datetime import date
    if date_value < date.today():
        raise serializers.ValidationError(
            _(f'{field_name} must be in the future')
        )
    
    return date_value


class ValidationMixin:
    """Mixin to add validation helpers to serializers"""
    
    def validate_email(self, value):
        """Standard email validation"""
        return validate_email_format(value)
    
    def validate_phone(self, value):
        """Standard phone validation"""
        return validate_phone_number(value)
    
    def validate_website(self, value):
        """Standard website validation"""
        return validate_website_url(value)
    
    def validate_first_name(self, value):
        """Validate first name"""
        return validate_name_field(value, "First name")
    
    def validate_last_name(self, value):
        """Validate last name"""
        return validate_name_field(value, "Last name")
    
    def validate_full_name(self, value):
        """Validate full name"""
        return validate_name_field(value, "Company name")