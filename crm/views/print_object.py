from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import DetailView

from crm.site.crmadminsite import crm_site


class PrintObjectView(DetailView):
    """Permission-checked detail view for the print previews.

    The print URLs used to be plain DetailViews, so any staff member
    could print any object by id, regardless of the object-level and
    department-level permissions that the admin enforces everywhere
    else. Reuse the ModelAdmin checks so the print preview can only
    be opened by users who may also view the object in the admin.
    """

    pk_url_kwarg = 'object_id'

    def get_queryset(self):
        model_admin = crm_site._registry[self.model]
        return model_admin.get_queryset(self.request)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.has_view_permission(obj):
            raise PermissionDenied
        return obj

    def has_view_permission(self, obj) -> bool:
        model_admin = crm_site._registry[self.model]
        return model_admin.has_view_permission(self.request, obj)


def print_object_view(model_name: str, template_name: str):
    return PrintObjectView.as_view(
        model=apps.get_model('crm', model_name),
        template_name=template_name
    )
