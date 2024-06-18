from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.models import UserProfile
from common.utils.helpers import add_chat_context
from common.utils.helpers import annotate_chat
from common.utils.helpers import LEADERS

icon_str = '<i class="material-icons" style="color: var(--body-quiet-color)">%s</i>'
chat_red_icon = '<i class="material-icons" style="font-size: 17px;color: var(--error-fg);">forum</i>'
chat_icon = '<i class="material-icons" style="font-size: 17px;color: var(--body-quiet-color);">forum</i>'
chat_link_str = '<a href="{}?content_type__id={}&object_id={}" title="{}" target="_blank">{}</a>'
contact_mail_icon = mark_safe(icon_str % 'contact_mail')
contact_phone_icon = mark_safe(icon_str % 'contact_phone')
person_icon = mark_safe(icon_str % 'person')
person_outline_icon = mark_safe(icon_str % 'account_box')
timezone_title = UserProfile._meta.get_field('utc_timezone').verbose_name  # NOQA
timezone_icon = mark_safe(
    f'<i title="{timezone_title}" class="material-icons" '
    f'style="color:var(--body-quiet-color)">watch_later</i>'
)
view_chat_str = _("View chat messages")


class UserProfileAdmin(admin.ModelAdmin):
    empty_value_display = LEADERS
    fields = (
        'contact_email',
        'pbx_number',
        'utc_timezone',
        'activate_timezone'
    )
    list_display = [
        'username',
        'chat_link',
        'user_full_name',
        'contact_email',
        'contact_phone',
    ]
    ordering = ('user__username',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email'
    )
    readonly_fields = ('contact_email', 'language_code')

    # -- ModelAdmin methods -- #

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = object_id
        content_type = ContentType.objects.get_for_model(UserProfile)
        add_chat_context(request, extra_context, object_id, content_type)
        return super().change_view(
            request, object_id, form_url,
            extra_context=extra_context,
        )

    def get_list_display(self, request):
        list_display = self.list_display
        if request.user.is_superuser:
            list_display = [*list_display, 'act']
        if settings.SHOW_USER_CURRENT_TIME_ZONE:
            list_display = [*list_display, 'timezone']
        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = annotate_chat(request, qs)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__is_active=True)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_view_permission(self, request, obj=None):
        return True

    # -- ModelAdmin Callables -- #
    
    @admin.display(description=_("Act"),
                   ordering='user__is_active',
                   boolean=True,)
    def act(self, obj):
        return obj.user.is_active

    @admin.display(description='')
    def chat_link(self, obj):
        value = ''
        content_type = ContentType.objects.get_for_model(self.model)
        url = reverse('site:chat_chatmessage_changelist')
        if getattr(obj, 'is_chat'):
            value = mark_safe(chat_link_str.format(
                url, content_type.id, obj.pk, view_chat_str, chat_icon))
        if getattr(obj, 'is_unread_chat'):
            value = mark_safe(chat_link_str.format(
                url, content_type.id, obj.pk, view_chat_str, chat_red_icon))
        return value

    @admin.display(description=_(contact_mail_icon),
                   ordering='user__email')
    def contact_email(self, obj):
        return obj.user.email

    @admin.display(description=contact_phone_icon)
    def contact_phone(self, obj):
        return obj.pbx_number

    @admin.display(description=person_outline_icon)
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description=timezone_icon)
    def timezone(self, obj):

        if obj.activate_timezone:
            return mark_safe(
                f'<div title="{timezone_title}" style="color:#ff8000">'
                f'{obj.get_utc_timezone_display()}</div>'
            )
        return mark_safe(
                f'<div title="{timezone_title}">'
                f'{settings.TIME_ZONE}</div>'
            )

    @admin.display(description=person_icon,
                   ordering='user__username')
    def username(self, obj):
        return obj.user.username
