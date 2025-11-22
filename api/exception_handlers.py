"""
Custom exception handlers for Django CRM API
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides more detailed error messages
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    request = context.get('request')
    if request:
        logger.error(
            f"API Exception: {exc} - Path: {request.path} - Method: {request.method}",
            exc_info=True
        )
    
    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            # Multiple field validation errors
            custom_response_data = {
                'error': 'Validation failed',
                'details': exc.message_dict,
                'status_code': 400
            }
        elif hasattr(exc, 'messages'):
            # Single field validation error
            custom_response_data = {
                'error': 'Validation failed',
                'details': {'non_field_errors': list(exc.messages)},
                'status_code': 400
            }
        else:
            custom_response_data = {
                'error': 'Validation failed',
                'details': {'non_field_errors': [str(exc)]},
                'status_code': 400
            }
        
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle IntegrityError (database constraints)
    if isinstance(exc, IntegrityError):
        custom_response_data = {
            'error': 'Data integrity error',
            'details': {
                'non_field_errors': ['This operation violates data constraints. Please check for duplicate entries.']
            },
            'status_code': 409
        }
        return Response(custom_response_data, status=status.HTTP_409_CONFLICT)
    
    # Handle 404 errors
    if isinstance(exc, Http404):
        custom_response_data = {
            'error': 'Not found',
            'details': {
                'non_field_errors': ['The requested resource was not found.']
            },
            'status_code': 404
        }
        return Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
    
    # If response is not None, enhance the default DRF error response
    if response is not None:
        custom_response_data = {
            'error': 'Request failed',
            'details': response.data if response.data else {},
            'status_code': response.status_code
        }
        
        # Add helpful messages for common errors
        if response.status_code == 400:
            custom_response_data['error'] = 'Validation failed'
            custom_response_data['help'] = 'Please check the provided data and try again.'
        elif response.status_code == 401:
            custom_response_data['error'] = 'Authentication required'
            custom_response_data['help'] = 'Please provide a valid authentication token.'
        elif response.status_code == 403:
            custom_response_data['error'] = 'Permission denied'
            custom_response_data['help'] = 'You do not have permission to perform this action.'
        elif response.status_code == 404:
            custom_response_data['error'] = 'Not found'
            custom_response_data['help'] = 'The requested resource could not be found.'
        elif response.status_code == 405:
            custom_response_data['error'] = 'Method not allowed'
            custom_response_data['help'] = 'This HTTP method is not supported for this endpoint.'
        elif response.status_code == 429:
            custom_response_data['error'] = 'Rate limit exceeded'
            custom_response_data['help'] = 'Please wait before making more requests.'
        elif response.status_code >= 500:
            custom_response_data['error'] = 'Internal server error'
            custom_response_data['help'] = 'Something went wrong on our end. Please try again later.'
        
        response.data = custom_response_data
    
    return response


def format_validation_errors(errors):
    """
    Format validation errors into a consistent structure
    """
    formatted_errors = {}
    
    for field, error_list in errors.items():
        if isinstance(error_list, list):
            formatted_errors[field] = [str(error) for error in error_list]
        elif isinstance(error_list, str):
            formatted_errors[field] = [error_list]
        else:
            formatted_errors[field] = [str(error_list)]
    
    return formatted_errors


class ValidationErrorResponse:
    """
    Helper class to create consistent validation error responses
    """
    
    @staticmethod
    def create(errors, status_code=400):
        """
        Create a validation error response
        """
        if isinstance(errors, str):
            errors = {'non_field_errors': [errors]}
        elif isinstance(errors, list):
            errors = {'non_field_errors': errors}
        
        return Response({
            'error': 'Validation failed',
            'details': format_validation_errors(errors),
            'status_code': status_code,
            'help': 'Please correct the errors and try again.'
        }, status=status_code)
    
    @staticmethod
    def field_error(field, message):
        """
        Create a single field validation error
        """
        return ValidationErrorResponse.create({field: [message]})
    
    @staticmethod
    def required_field(field):
        """
        Create a required field error
        """
        return ValidationErrorResponse.field_error(field, 'This field is required.')
    
    @staticmethod
    def invalid_choice(field, value, choices):
        """
        Create an invalid choice error
        """
        choices_str = ', '.join(str(choice) for choice in choices[:5])
        if len(choices) > 5:
            choices_str += ', ...'
        
        message = f"'{value}' is not a valid choice. Available choices: {choices_str}"
        return ValidationErrorResponse.field_error(field, message)


class SuccessResponse:
    """
    Helper class to create consistent success responses
    """
    
    @staticmethod
    def create(data=None, message="Operation completed successfully", status_code=200):
        """
        Create a success response
        """
        response_data = {
            'success': True,
            'message': message,
            'status_code': status_code
        }
        
        if data is not None:
            response_data['data'] = data
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(data, message="Resource created successfully"):
        """
        Create a 201 Created response
        """
        return SuccessResponse.create(data, message, 201)
    
    @staticmethod
    def updated(data, message="Resource updated successfully"):
        """
        Create a 200 Updated response
        """
        return SuccessResponse.create(data, message, 200)
    
    @staticmethod
    def deleted(message="Resource deleted successfully"):
        """
        Create a 204 Deleted response
        """
        return Response({
            'success': True,
            'message': message,
            'status_code': 204
        }, status=204)