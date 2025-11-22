from rest_framework.permissions import BasePermission, SAFE_METHODS


class OwnedObjectPermission(BasePermission):
    """
    Grants access if user is staff/superuser or related through owner,
    co_owner, responsible/subscribers, or department membership.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        owner = getattr(obj, 'owner', None)
        co_owner = getattr(obj, 'co_owner', None)
        if owner == user or co_owner == user:
            return True

        if hasattr(obj, 'responsible') and obj.responsible.filter(id=user.id).exists():
            return True
        if hasattr(obj, 'subscribers') and obj.subscribers.filter(id=user.id).exists():
            return True

        department = getattr(obj, 'department', None)
        if department and department in user.groups.all():
            return True

        # Allow safe reads for partner relations like contact.company owner?
        if request.method in SAFE_METHODS:
            company = getattr(obj, 'company', None)
            if company and getattr(company, 'owner', None) == user:
                return True

        return False
