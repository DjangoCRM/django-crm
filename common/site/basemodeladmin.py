import re
from django.contrib import admin
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from common.models import Reminder
from common.views.export_objects import export_selected_objects
from common.utils.helpers import get_department_id
from common.utils.helpers import OBJ_DOESNT_EXIT_STR
from common.utils.helpers import get_verbose_name
from common.utils.helpers import get_today
from common.utils.helpers import LEADERS
from crm.utils.helpers import add_id_to_raw_id_field_label

TAGS_STR = _('Tags')
add_tags_str = _("Add tags")
creation_date_str = _("Creation date")
export_selected_str = _("Export selected objects")
next_step_deadline_str = _("Next step deadline")
safe_next_step_deadline_icon = mark_safe(
        f'<i class="material-icons" title="{next_step_deadline_str}" '
        f'style="color: var(--body-quiet-color)">event_busy</i>'
)
TODAY_ICON = '<i class="material-icons" title="{}" style="color: var(--body-quiet-color)">today</i>'
white_tag_icon = '<i class="material-icons" style="color: var(--primary-fg)">local_offer</i>'
grey_tag_icon = '<i class="material-icons" style="color: var(--body-quiet-color)">local_offer</i>'
blue_tag_icon = '<i class="material-icons" style="color: var(--primary)">local_offer</i>'
safe_attach_file_icon = mark_safe(
                '<i class="material-icons" style="color: var(--body-quiet-color)">attach_file</i>'
)
safe_person_icon = mark_safe(
            '<i class="material-icons" title="Owner" style="color: var(--body-quiet-color)">person</i>'
)
safe_creation_date_icon = mark_safe(TODAY_ICON.format(creation_date_str))


class BaseModelAdmin(admin.ModelAdmin):
    empty_value_display = LEADERS
    show_facets = admin.ShowFacets.NEVER
    save_on_top = True

    # -- ModelAdmin methods -- #

    def delete_model(self, request, obj):
        try:
            files = obj.files.all()
            if files:
                for f in files:
                    f.delete()
        except AttributeError:
            pass
        super().delete_model(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        add_id_to_raw_id_field_label(self, form)
        return form

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            st = " ".join(search_term.splitlines()).strip()
            if re.match(r"^[iI][dD]\s*\d+$", st):
                return self.model.objects.filter(id=st[2:]), True

            if re.match(r"^ticket:*\s*", st):
                if hasattr(self.model, 'ticket'):
                    ticket = re.sub(r"^ticket:*\s*", '', st)
                    return self.model.objects.filter(ticket=ticket), True
            messages.warning(
                request,
                _("Filters may affect search results.")
            )
        return super().get_search_results(request, queryset, search_term)

    def save_model(self, request, obj, form, change):
        self.set_owner(request, obj)
        super().save_model(request, obj, form, change)

    # -- ModelAdmin actions -- #

    @admin.display(description=export_selected_str)
    def export_selected(self, request, queryset):
        return export_selected_objects(request, queryset)

    # -- ModelAdmin Callables -- #

    @admin.display(description=_("Act"),
                   ordering='active',
                   boolean=True,)
    def act(self, obj):
        return obj.active

    @admin.display(description='')
    def attachment(self, obj):
        if obj.files.exists():
            return safe_attach_file_icon
        return ''

    @admin.display(description=safe_next_step_deadline_icon)
    def coloured_next_step_date(self, obj):
        field = 'next_step_date'
        # 'step_date' is annotation for Task and Projects
        if hasattr(obj, 'step_date') \
                and hasattr(obj, 'task') \
                and not obj.task:
            field = 'step_date'
        step_date = date_format(
            getattr(obj, field), format='SHORT_DATE_FORMAT', use_l10n=True
        )
        if not obj.active:
            return mark_safe(
                f'<div title="{next_step_deadline_str}">{step_date}</div>'
            )
        color = 'gray'
        if getattr(obj, field) < get_today():
            color = 'var(--error-fg)'
        return mark_safe(
            f'<div title="{next_step_deadline_str}" '
            f'style="color:{color}">{step_date}</div>'
        )

    @admin.display(description=safe_creation_date_icon,
                   ordering='creation_date')
    def created(self, obj):
        title = get_verbose_name(obj, "creation_date")
        value = date_format(
            obj.creation_date.date(),
            format="SHORT_DATE_FORMAT",
            use_l10n=True
        )
        return mark_safe(
            f'<div title="{title}">{value}</div>'
        )

    @admin.display(description=mark_safe(
            '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
        ), ordering='name')
    def name_icon(self, obj):
        return obj.name

    @admin.display(description=safe_person_icon, ordering='owner')
    def person(self, obj):
        if getattr(obj, 'co_owner', None):
            return f'{obj.owner}, {obj.co_owner}'
        else:
            return obj.owner

    @admin.display(description=mark_safe(
        f'{grey_tag_icon} {TAGS_STR}'
    ))
    def tag_list(self, obj):
        tag_names = obj.tags.all().values_list('name', flat=True)
        tags = [f"{blue_tag_icon}{x}&nbsp" for x in tag_names]
        return mark_safe(' '.join(tags) if tags else '')

    @admin.display(description=_('Workflow'))
    def workflow_area(self, obj):
        text = obj.workflow
        return mark_safe(
            f'<textarea name="workflow_area" cols="80" rows="8" '
            f'class="vLargeTextField">{text}</textarea>'
        )

    # -- Custom methods -- #

    @staticmethod
    def add_remainder_context(request: WSGIRequest, extra_context: dict,
                              object_id: int, content_type) -> None:
        extra_context['is_reminder'] = Reminder.objects.filter(
            active=True,
            object_id=object_id,
            content_type=content_type,
            owner=request.user
        ).exists()

    def get_tag_fieldsets(self, obj=None):
        """Hides the tag list if it is empty"""
        tag_fieldsets = []
        if hasattr(self.model, 'tags'):
            tag_fieldsets.append(
                (mark_safe(f'{white_tag_icon} {add_tags_str}'),
                    {
                        'classes': ('collapse',),
                        'fields': ('tags',)
                    })
            )
            if obj and obj.tags.exists():
                tag_fieldsets.insert(0, (None, {'fields': ('tag_list',)}))
        return tag_fieldsets

    def get_url_if_no_object(self, request: WSGIRequest, object_id: int) -> str:
        try:
            self.model.objects.get(id=object_id)
        except self.model.DoesNotExist:
            messages.error(
                request,
                OBJ_DOESNT_EXIT_STR.format(
                    self.model._meta.verbose_name, object_id    # NOQA
                )
            )
            return (
                reverse(
                    f"site:{self.opts.app_label}_"
                    f"{self.model.__name__.lower()}_changelist"
                )
            )
        return ''

    @staticmethod
    def set_owner(request: WSGIRequest, obj):
        if request.user.is_authenticated:
            obj.modified_by = request.user
            if not obj.owner:
                obj.owner = request.user
            if hasattr(obj, 'department') and not obj.department:
                if obj.owner:
                    obj.department_id = get_department_id(obj.owner)
                else:
                    obj.department_id = request.user.department_id  # NOQA
