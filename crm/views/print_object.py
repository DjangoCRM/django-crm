from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic.detail import DetailView

from crm.site.crmadminsite import crm_site


class PrintObjectView(DetailView):
    """
    Print view of a CRM object (email, request).
    Applies the same access checks as the object's page in the CRM site:
    the object is fetched through the model admin's queryset and the user
    must have the view (or change) permission for it.
    """
    pk_url_kwarg = 'object_id'

    def get_object(self, queryset=None):
        model_admin = crm_site.get_model_admin(self.model)
        obj = model_admin.get_object(
            self.request, str(self.kwargs[self.pk_url_kwarg])
        )
        if obj is None:
            raise Http404
        if not model_admin.has_view_or_change_permission(self.request, obj):
            raise PermissionDenied
        return obj
