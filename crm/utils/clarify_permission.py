from typing import Any

from django.core.handlers.wsgi import WSGIRequest


def clarify_permission(request: WSGIRequest, obj: Any) -> bool:
    """
    Clarifies the permissions for the current user on the object.
    """

    # To cover cases where the current user has multiple roles
    # e.g. super operator & manager
    if any((
            request.user.is_chief,              # NOQA
            request.user.is_superoperator,      # NOQA
            request.user.is_superuser
    )):
        return True

    if request.user.is_operator and obj.department_id == request.user.department_id:  # NOQA
        return True

    if hasattr(obj, 'owner'):
        if request.user == obj.owner:
            return True
        if hasattr(obj, 'co_owner') and request.user in (obj.owner, obj.co_owner):
            return True
    return False
