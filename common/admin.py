import re
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.models import Department
from common.models import Reminder
from common.models import TheFile
from common.models import UserProfile
from common.site import reminderadmin
from common.site import userprofileadmin
from crm.site.crmadminsite import crm_site
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter


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


class ReminderAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
        'reminder_date',
        'active',
        'owner',
        'content_type'
    )
    list_filter = (
        'active',
        ('owner', ScrollRelatedOnlyFieldListFilter)
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


class TheFileWidget(forms.ClearableFileInput):
    initial_text = ''
    template_name = 'common/widgets/clearable_file_input.html'


class InlineFileForm(ModelForm):
    class Meta:
        model = TheFile
        fields = ('file',)
        widgets = {'file': TheFileWidget}
        labels = {'file': ''}


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
    list_display = ('id', 'content_type', 'object_id', 'to_object', 'file_name')
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


class FileInline(GenericStackedInline):
    form = InlineFileForm
    model = TheFile
    icon = '<i class="material-icons" style="color: var(--primary-fg)">attach_file</i>'
    name_plural = model._meta.verbose_name_plural
    verbose_name_plural = mark_safe(f'{icon} {name_plural}')
    fields = ('file',)
    extra = 0

    # -- GenericStackedInline methods -- #

    def has_add_permission(self, request, obj):
        # who can change parent object should
        # have permission to add inline
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if not value or not obj:
            return value
        return self.clarify_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # who can change parent object should
        # have permission to delete inline
        return self.has_change_permission(request, obj)

    # -- Custom methods -- #

    @staticmethod
    def clarify_permission(request, obj):
        if hasattr(obj, 'owner'):
            if obj.owner == request.user or not obj.owner:
                if any((hasattr(obj, 'REVIEWED') and obj.stage == obj.REVIEWED,
                        hasattr(obj, 'incoming') and obj.incoming,
                        hasattr(obj, 'uid') and obj.uid,
                        not obj.owner and request.user.is_chief)):
                    return False
                return True
        else:
            return True

        if hasattr(obj, 'co_owner') and obj.co_owner == request.user \
                or request.user.is_superoperator \
                or request.user.is_task_operator \
                or request.user.is_superuser \
                or hasattr(obj, 'department') and request.user.is_operator \
                and obj.department_id == request.user.department_id \
                or hasattr(obj, 'responsible') and obj.responsible.count() == 1 \
                and request.user in (obj.responsible.all()) \
                or hasattr(obj, 'win_closing_date') and request.user.is_chief:
            return True

        return False


class UserProfileAdmin(userprofileadmin.UserProfileAdmin):
    fields = ('user', 'pbx_number', 'utc_timezone', 'activate_timezone')


crm_site.register(Reminder, reminderadmin.ReminderAdmin)
crm_site.register(UserProfile, userprofileadmin.UserProfileAdmin)

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(TheFile, TheFileAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
