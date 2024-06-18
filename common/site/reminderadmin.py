from urllib.parse import urlencode
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from common.models import Reminder
from common.forms.reminderform import ReminderForm

icon_str = '<i title="%s" class="material-icons" style="color: var(--body-quiet-color)">%s</i>'
creation_date_title = Reminder._meta.get_field('creation_date').verbose_name  # NOQA
creation_date_icon = mark_safe(icon_str % (creation_date_title, 'insert_invitation'))
reminder_date_title = Reminder._meta.get_field('reminder_date').verbose_name  # NOQA
reminder_date_icon = mark_safe(icon_str % (reminder_date_title, 'event_available'))
reminders_title = Reminder._meta.verbose_name_plural  # NOQA
alarm_icon = mark_safe(icon_str % (reminders_title, 'alarm'))
to_object_icon = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
)


class ReminderAdmin(admin.ModelAdmin):
    actions = ('delete_selected',)
    fieldsets = ((None, {
            'fields': (
                'to_object', 'subject',
                'description', 'reminder_date',
                ('active', 'send_notification_email'),
            )
        }),)
    form = ReminderForm
    list_display = (
        'iconed_subject',
        'iconed_reminder_date',
        'active', 'to_object',
        'iconed_creation_date'
    )
    readonly_fields = ('owner', 'to_object')
    save_on_top = False
    search_fields = ('subject', 'description')

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        initial = dict(request.GET.items())
        if initial.get('content_type__id__exact', None):
            extra_context['content_type_id'] = int(initial.get('content_type__id__exact'))
            extra_context['object_id'] = int(initial.get('object_id'))
        return super().changelist_view(request, extra_context)

    def get_changeform_initial_data(self, request):
        object_id = request.GET.get('object_id')
        content_type_id = request.GET.get('content_type')
        content_type = ContentType.objects.get(pk=content_type_id)
        content_object = content_type.get_object_for_this_type(pk=object_id)
        return {"subject": content_object.name}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(owner=request.user)

    def response_add(self, request, obj, post_url_continue=None):
        if '_popup' in request.POST:
            return HttpResponse('<script type="text/javascript">window.close()</script>')
        return self.redirect_to_changelist(obj)

    def save_model(self, request, obj, form, change):
        if not change:
            changelist_filters = request.GET.get('_changelist_filters')
            if changelist_filters:
                data = changelist_filters.split('&')
                obj.content_type_id = int(data[0].lstrip('content_type__id__exact='))
                obj.object_id = int(data[1].lstrip('object_id='))
            else:
                obj.content_type_id = request.GET.get('content_type')
                obj.object_id = request.GET.get('object_id')
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    # -- ModelAdmin callables -- #

    @admin.display(
        description=creation_date_icon,
        ordering='creation_date'
    )
    def iconed_creation_date(self, obj):
        return obj.creation_date

    @admin.display(
        description=reminder_date_icon,
        ordering='reminder_date'
    )
    def iconed_reminder_date(self, obj):
        return obj.reminder_date

    @admin.display(description=alarm_icon, ordering='subject')
    def iconed_subject(self, obj):
        return obj.subject

    @staticmethod
    @admin.display(description=to_object_icon)
    def to_object(obj):
        instance = obj.content_object
        name = instance._meta.verbose_name  # NOQA
        url = reverse(
            f"site:{instance._meta.app_label}_{instance._meta.model_name}_change",  # NOQA
            args=(instance.id,)
        )
        return mark_safe(
            f'<a href="{url}" target="blank">{name}: {instance}</a>'
        )

    # -- Custom methods -- #

    @staticmethod
    def redirect_to_changelist(obj):
        params = {
            'content_type__id__exact': obj.content_type_id,
            'object_id': obj.object_id
        }
        return HttpResponseRedirect(
            reverse(
                "site:common_reminder_changelist"
            ) + f'?{urlencode(params)}'
        )
