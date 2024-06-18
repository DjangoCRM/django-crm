from django.template.defaultfilters import linebreaks
from django.utils.safestring import mark_safe
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from massmail.models import EmlAccountsQueue


class EmailAccountAdmin(CrmModelAdmin):
    list_display = (
        'name', 'id', 'last_import_dt', 'today_count', 'today_date',
        'massmail', 'br_report', 'main', 'do_import', 'owner'
    )
    
    readonly_fields = ('creation_date', 'update_date',)
    fieldsets = (
        (None, {
            'fields': (
                'name', 'main', 'massmail', 'do_import',
                'email_host', 'imap_host', 'email_host_user',
                'email_host_password', 'email_app_password', 'email_port',
                'from_email', 'email_use_tls', 'email_use_ssl',
                'email_imail_ssl_certfile', 'email_imail_ssl_keyfile',
                'refresh_token'
            )
        }),
        ('Additional information', {
            'classes': ('collapse',),
            'fields': (
                ('owner', 'co_owner', 'modified_by'), 'department',
                ('creation_date', 'update_date',)
            )
        }),
    )
    save_as = True

    # -- ModelAdmin methods -- #

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)
    
    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            list_filter.append(ByOwnerFilter)
            return list_filter
        return []

    def has_view_permission(self, request, obj=None):
        if not obj:
            return super().has_view_permission(request, obj=None)
        if request.user.is_superuser:
            return True
        if obj.owner == request.user:
            return True
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        queue_obj, _ = EmlAccountsQueue.objects.get_or_create(
            owner=obj.owner)
        if obj.massmail and not obj.main:
            queue_obj.add_id(obj.pk)

        if change:
            if 'main' in form.changed_data and obj.main:
                queue_obj.remove_id(obj.pk)
            if 'owner' in form.changed_data:
                queue_objs = EmlAccountsQueue.objects.all()
                for qobj in queue_objs:
                    qobj.remove_id(obj.pk)

    # -- ModelAdmin actions -- #

    def br_report(self, instance):
        return mark_safe(linebreaks(instance.report))
