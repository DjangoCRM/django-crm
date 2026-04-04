from PIL import Image
from PIL import ImageDraw
from io import BytesIO

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from common.forms.userprofileform import UserProfileForm
from common.models import UserProfile
from common.utils.chat_link import get_chat_link
from common.utils.helpers import add_chat_context
from common.utils.helpers import annotate_chat
from common.utils.helpers import LEADERS

icon_str = '<i class="material-icons" style="color: var(--body-quiet-color)">%s</i>'
contact_mail_icon = mark_safe(icon_str % 'contact_mail')
contact_phone_icon = mark_safe(icon_str % 'contact_phone')
person_icon = mark_safe(icon_str % 'person')
person_outline_icon = mark_safe(icon_str % 'account_box')
avatar_icon = mark_safe(icon_str % 'face')
timezone_title = UserProfile._meta.get_field('utc_timezone').verbose_name  # NOQA
timezone_icon = mark_safe(
    f'<i title="{timezone_title}" class="material-icons" '
    f'style="color:var(--body-quiet-color)">watch_later</i>'
)
view_chat_str = _("View chat messages")


class UserProfileAdmin(admin.ModelAdmin):
    empty_value_display = ''
    form = UserProfileForm
    list_display = [
        'username',
        'chat_link',
        'user_full_name',
        'contact_email',
        'contact_phone',
        'language',
    ]
    ordering = ('user__username',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email'
    )
    readonly_fields = (
        'contact_email',
        'language',
        'avatar_preview',
        'show_timezone'
    )

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

    def get_fieldsets(self, request, obj=None):
        fields = []
        if request.user.is_superuser:
            fields.append('is_active')
        fields.append('avatar_preview')
        if request.user == obj.user or request.user.is_superuser:
            fields.append('avatar')
        fields.extend(['contact_email', 'pbx_number'])
        if request.user == obj.user:
            fields.extend(
                ['language_code', ('utc_timezone',  'activate_timezone')])
        else:
            fields.extend(['language', 'show_timezone'])
        return [(None, {"fields": fields})]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        is_active_field = User._meta.get_field('is_active')
        if request.user.is_superuser:
            form.base_fields['is_active'].initial = obj.user.is_active
            form.base_fields['is_active'].label = is_active_field.verbose_name
            form.base_fields['is_active'].help_text = is_active_field.help_text
        if request.user == obj.user:
            form.base_fields['language_code'].initial = obj.language_code
            form.base_fields['language_code'].label = _('Language')
            form.base_fields['language_code'].widget = forms.Select(
                choices=settings.LANGUAGES)

        return form

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

    def response_change(self, request, obj):
        if getattr(obj, 'language_code_changed', False):
            # If language was changed, redirect to the same page to apply new language
            url = ''
            if '_save' in request.POST:
                url = reverse('site:common_userprofile_changelist')
            elif '_continue' in request.POST:
                url = reverse('site:common_userprofile_change', args=[obj.pk])
            if url:
                query_string = request.META.get('QUERY_STRING', '')
                return HttpResponseRedirect(f"{url}?{query_string}")
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        if 'language_code' in form.changed_data:
            # Activate selected language
            obj.language_code_changed = True
            activate(obj.language_code)

        # Delete old avatar file if new one is being uploaded
        if change and 'avatar' in form.changed_data:
            try:
                old_profile = UserProfile.objects.get(pk=obj.pk)
                if old_profile.avatar and old_profile.avatar != obj.avatar:
                    old_profile.avatar.delete(save=False)
            except UserProfile.DoesNotExist:
                pass

        # Resize new avatar if present
        if 'avatar' in form.changed_data and obj.avatar:
            resize_avatar(obj)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if 'is_active' in form.changed_data:
            user = form.instance.user
            user.is_active = form.cleaned_data.get('is_active')
            user.save(update_fields=['is_active'])

    # -- ModelAdmin Callables -- #

    @admin.display(description='')
    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" style="width:200px;height:200px;border-radius:50%">')
        return mark_safe(
            '<i class="material-icons" style="font-size: 200px;vertical-align: middle;border-radius:50%;color: var(--body-quiet-color)">face</i>'
        )

    @admin.display(description=_("Act"),
                   ordering='user__is_active',
                   boolean=True,)
    def act(self, obj):
        return obj.user.is_active

    @admin.display(description='')
    def chat_link(self, obj):
        return get_chat_link(obj)

    @admin.display(description=_(contact_mail_icon),
                   ordering='user__email')
    def contact_email(self, obj):
        return obj.user.email

    @admin.display(description=contact_phone_icon)
    def contact_phone(self, obj):
        if obj.pbx_number:
            return obj.pbx_number
        return LEADERS

    @admin.display(description=_('Language'))
    def language(self, obj):
        lang = next((
            lang[1] for lang in settings.LANGUAGES
            if lang[0] == obj.language_code
        ), LEADERS)
        return lang

    @admin.display(description=_("UTC time zone"))
    def show_timezone(self, obj):
        if obj.utc_timezone:
            return obj.obj.utc_timezone
        return settings.TIME_ZONE

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

    @admin.display(description=person_outline_icon)
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description=person_icon,
                   ordering='user__username')
    def username(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" '
                'style="vertical-align: middle;'
                'width:50px;height:50px;border-radius:50%">'
                f' {obj.user.username}'
            )
        return mark_safe(
            f'<i class="material-icons" '
            'style="font-size:50px;vertical-align:middle;'
            'border-radius:50%;color:var(--body-quiet-color)"'
            f'>face</i> {obj.user.username}'
        )

# -- Custom Methods -- #


def resize_avatar(obj) -> None:
    """
    Resize uploaded avatar image to a maximum of 200x200 pixels.
    """
    if obj.avatar:
        img = Image.open(obj.avatar)
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Create circular mask
        size = img.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, size[0], size[1]], fill=255)
        img.putalpha(mask)

        # Save to BytesIO
        resized_image = BytesIO()
        img.save(resized_image, format='PNG', quality=85)
        resized_image.seek(0)

        # Create a new File object
        obj.avatar.file = resized_image
        obj.avatar.name = f"{obj.user.username}.png"
