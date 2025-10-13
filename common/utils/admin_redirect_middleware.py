from django.conf import settings
from django.http import HttpResponseRedirect


class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the admin site and the user is not a superuser
        if settings.SECRET_ADMIN_PREFIX in request.path and not request.user.is_superuser:
            # Remove the '/admin' prefix and redirect to the CRM site's URL
            new_path = request.path.replace(
                settings.SECRET_ADMIN_PREFIX, settings.SECRET_CRM_PREFIX)
            query_string = request.META.get('QUERY_STRING')
            if query_string:
                new_path = f"{new_path}?{query_string}"
            return HttpResponseRedirect(new_path)
        return self.get_response(request)
