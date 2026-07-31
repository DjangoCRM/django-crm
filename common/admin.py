import re
from django import forms
from django.contrib import admin
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.models import Department
from common.models import Reminder
from common.models import TheFile
from common.models import UserProfile
from common.site import reminderadmin
from common.site import userprofileadmin
from sharedkernel.search import AuditSearchService


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'default_country',
                'default_currency',
                'works_globally',

            )
        }),
    )


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "content_type",
                    "action_time", 'object_id')
    list_display_links = ("__str__",)
    list_filter = ('action_flag', 'action_time', 'user', 'content_type')
    search_fields = ('change_message',)

    def get_search_results(self, request, queryset, search_term):
        normalized = ' '.join(search_term.splitlines()).strip()
        if not normalized:
            return super().get_search_results(request, queryset, search_term)
        return AuditSearchService.search(queryset, search_term)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReminderAdmin(admin.ModelAdmin):
    owner_list_filter = admin.RelatedFieldListFilter
    list_display = (
        'subject',
        'reminder_date',
        'active',
        'owner',
        'content_type'
    )
    raw_id_fields = ('owner', 'content_type')
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': (
                'subject', 'description', 'reminder_date',
                ('active', 'send_notification_email'),
                'owner',
            )
        }),
        (None, {
            'fields': (
                'content_type', 'object_id',
            )
        }),
    )

    def get_list_filter(self, request):
        return (
            'active',
            ('owner', self.owner_list_filter),
        )


class TheFileForm(ModelForm):
    class Meta:
        model = TheFile
        fields = ('content_type', 'object_id', 'file', 'file_name')

    file_name = forms.CharField(
        required=False,
        help_text=_(
            "You can specify the name of an existing file on the server"
            " along with the path instead of uploading it."
        )
    )

    def save(self, commit=True):
        if 'file_name' in self.changed_data:
            self.instance.file.name = self.cleaned_data['file_name']
        super().save(commit)
        return self.instance


class TheFileAdmin(admin.ModelAdmin):
    form = TheFileForm
    list_display = ('id', 'content_type', 'object_id',
                    'to_object', 'file_name')
    search_fields = ('id', 'object_id', 'file')
    list_filter = ('content_type',)
    read_only = ('file_url', 'to_object')

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            st = " ".join(search_term.splitlines()).strip()
            if re.match(r"^[iI][dD]\s*\d+$", st):
                return self.model.objects.filter(id=st[2:]), True
        return super().get_search_results(request, queryset, search_term)

    # -- ModelAdmin callables -- #

    @staticmethod
    @admin.display(description='object')
    def to_object(instance):
        obj = instance.content_object
        url = obj.get_absolute_url()
        return mark_safe(
            f'<a href="{url}" target="_blank">{obj}</a>'
        )

    @staticmethod
    def file_name(instance):
        return instance.file.name


class UserProfileAdmin(userprofileadmin.UserProfileAdmin):
    fields = ('user', 'pbx_number', 'utc_timezone', 'activate_timezone')

    # -- ModelAdmin methods -- #

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        list_display.extend(('staff', 'superuser'))
        return list_display

    # -- ModelAdmin Callables -- #

    @admin.display(description=_('staff'),
                   ordering="user__is_staff",
                   boolean=True, )
    def staff(self, obj):
        return obj.user.is_staff

    @admin.display(description=_('superuser'),
                   ordering="user__is_superuser",
                   boolean=True, )
    def superuser(self, obj):
        return obj.user.is_superuser


def register_shared_models_on_crm_site() -> None:
    from sharedkernel.adminsites import CRM_SITE_NAME
    from sharedkernel.adminsites import get_admin_site

    crm_admin_site = get_admin_site(CRM_SITE_NAME)
    crm_admin_site.register(Reminder, reminderadmin.ReminderAdmin)
    crm_admin_site.register(UserProfile, userprofileadmin.UserProfileAdmin)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(admin.models.LogEntry, LogEntryAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(TheFile, TheFileAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
