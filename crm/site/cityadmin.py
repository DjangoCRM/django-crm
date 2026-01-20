from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from crm.utils.admfilters import ByCountryFilter


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = (ByCountryFilter,)
    ordering = ('name', 'country')
    search_fields = ('name', 'alternative_names')

    # -- ModelAdmin methods -- #

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        content_type_id = ContentType.objects.get_for_model(self.model).id
        url = reverse("delete_duplicate", args=(content_type_id, object_id))
        query_string = request.META.get('QUERY_STRING', '')
        if query_string:
            url = f"{url}?{query_string}"
        extra_context['del_dup_url'] = url
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
