from urllib.parse import urlencode
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from common.admin import FileInline
from common.site.basemodeladmin import BaseModelAdmin
from common.utils.email_to_participants import email_to_participants
from common.utils.helpers import add_chat_context
from common.utils.helpers import CONTENT_COPY_ICON
from common.utils.helpers import CONTENT_COPY_LINK
from common.utils.helpers import COPY_STR
from common.utils.helpers import USER_MODEL
from common.utils.helpers import compose_subject
from common.utils.helpers import get_active_users
from common.utils.helpers import get_today
from common.utils.helpers import get_verbose_name
from common.utils.helpers import LEADERS
from common.utils.helpers import notify_admins_no_email
from common.utils.helpers import save_message
from crm.utils.admfilters import ByOwnerFilter
from tasks.forms import MemoForm
from tasks.models import Memo
from tasks.utils.admfilters import ByToFilter
from tasks.utils.admfilters import TaskTagFilter


copy_str = _('Copy')
department_str = _('Department')
draft_str = _('draft')
event_available_icon = '<i class="material-icons" title="{}">event_available</i>'
overdue_str = _('overdue')
postponed_str = _('postponed')
status_str = _('Status')
subscribers_subject = _("You are subscribed to a new office memo")
reviewed_str = _('reviewed')
unreviewed_str = _('unreviewed')


class MemoAdmin(BaseModelAdmin):

    filter_horizontal = ('subscribers',)
    form = MemoForm
    inlines = [FileInline]
    list_filter = (
        'stage',
        ByToFilter,
        ByOwnerFilter,
        'creation_date',
        TaskTagFilter
    )
    list_per_page = 50
    raw_id_fields = ('task', 'project', 'deal')
    readonly_fields = [
        'name_icon',
        'creation_date',
        'owner',
        'modified_by',
        'status',
        'action',
        'date_of_review',
        'view_button',
        'department',
        'attachment',
        'content_copy',
        "subscribers_list",
    ]
    search_fields = ('name', 'description', 'note')
    radio_fields = {'stage': admin.HORIZONTAL}

    # -- ModelAdmin methods -- #

    def change_view(self, request, object_id, form_url='', extra_context=None):
        url = self.get_url_if_no_object(request, object_id)
        if url:
            return HttpResponseRedirect(url)
        content_type = ContentType.objects.get_for_model(Memo)
        extra_context = extra_context or {}
        extra_context['content_type_id'] = content_type.id
        add_chat_context(request, extra_context, object_id, content_type)
        self.add_remainder_context(
            request, extra_context, object_id, content_type)
        deal_id = Memo.objects.get(id=object_id).deal_id
        if deal_id and request.user.has_perm('crm.view_deal'):
            extra_context['deal_url'] = reverse(
                "site:crm_deal_change", args=(deal_id,)
            )
        url = reverse("site:tasks_memo_add") + f"?copy_memo={object_id}"
        extra_context['content_copy_link'] = mark_safe(
            CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        deal_id = request.GET.get('deal__id__exact')
        if deal_id:
            extra_context['deal_id'] = deal_id
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def delete_model(self, request, obj):
        subject = _("Your office memo has been deleted")
        message = f"{subject} ({request.user.username}): {obj.name}"
        owner = obj.owner
        super().delete_model(request, obj)
        if not settings.DEBUG and owner != request.user:
            if hasattr(obj.owner, 'email'):
                owner.email_user(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    fail_silently=False,
                )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'to':
            if not any((request.user.is_superuser, request.user.is_task_operator)):
                kwargs["queryset"] = USER_MODEL.objects.filter(
                    groups__name__in=(
                        'chiefs', 'department heads', 'task_operators')
                ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "subscribers":
            kwargs["queryset"] = get_active_users().order_by("username")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        memo_id = request.GET.get('copy_memo')
        if memo_id:
            memo = Memo.objects.get(id=memo_id)
            initial['name'] = memo.name
            initial['to'] = memo.to
            initial['description'] = memo.description
            initial['subscribers'] = memo.subscribers.all()
            if memo.deal:
                initial['deal'] = memo.deal
            if memo.resolution:
                initial['resolution'] = memo.resolution

        return initial

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': [
                    'name',
                    ('to', 'resolution'),
                    'description',
                    ('owner', 'modified_by'),
                ]
            }),
            (_("Change subscribers"), {
                "classes": ("collapse",), "fields": ("subscribers",)
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': ('task', 'project', 'deal')
            }),
        ]
        if obj:
            if any((
                    request.user.is_superuser,
                    request.user.is_chief,
                    request.user.is_task_operator
            )):
                fieldsets[0][1]['fields'].insert(
                    1, ('creation_date', 'stage'))
            else:
                if request.user == obj.owner:
                    fieldsets[0][1]['fields'].insert(1, ('creation_date', 'draft'))
                else:
                    fieldsets[0][1]['fields'].insert(1, 'creation_date')
            fieldsets[0][1]['fields'].insert(4, 'note')
            if any((obj.task, obj.project, obj.deal)):
                fieldsets[0][1]['fields'].insert(5, 'view_button')
                if obj.subscribers.exists():
                    fieldsets.append(
                        (None, {"fields": ("subscribers_list",)}),
                    )
        else:
            fieldsets[0][1]['fields'].insert(1, ('creation_date', 'draft'))
        return fieldsets

    def get_list_display(self, request):
        if request.user.is_chief:
            return (
                'name_icon',
                'attachment',
                'person',
                'status',
                'date_of_review',
                'action',
                'to',
                'department',
                'created'
            )
        return (
            'name_icon',
            'attachment',
            'to',
            'status',
            'date_of_review',
            'action',
            'person',
            'department',
            'created',
            'content_copy'
        )

    def get_queryset(self, request):
        self.today = get_today()  # NOQA
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if any((
                    request.user.is_chief,
                    request.user.is_task_operator
            )):
                qs = qs.exclude(Q(draft=True) & ~Q(owner=request.user))
            else:
                qs = qs.filter(
                    Q(to=request.user) & Q(draft=False)
                    | Q(owner=request.user)
                    | Q(subscribers=request.user)
                )
        qs = qs.annotate(department=Subquery(
            USER_MODEL.objects.filter(
                id=OuterRef('owner__pk'),
                groups__department__isnull=False
            ).values('groups__name')[:1]
        )).distinct()
        return qs

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj:
            if any((
                    request.user.is_superuser,
                    request.user.is_chief,
                    request.user.is_task_operator
            )):
                return True
            if obj.owner == request.user:
                return False if obj.stage == obj.REVIEWED else True
        return True

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj:
            return self.has_change_permission(request, obj)
        return True

    def has_view_permission(self, request, obj=None):
        value = super().has_view_permission(request, obj)
        if value is False or not obj:
            return value

        if not obj.draft:
            if request.user in (
                    obj.owner, obj.to, obj.subscribers.all()
            ) or any((
                    request.user.is_chief,
                    request.user.is_task_operator,
                    request.user.is_superuser
            )):
                return True
        else:
            if request.user == obj.owner:
                return True
        return False

    def response_post_save_add(self, request, obj):
        if '_popup' in request.POST:
            return HttpResponse(
                '<script type="text/javascript">window.close()</script>'
            )
        url = reverse("site:tasks_memo_changelist")
        params = ''
        if obj.deal:
            params = f'?deal__id__exact={obj.deal_id}'
        return HttpResponseRedirect(url + params)

    def response_post_save_change(self, request, memo):
        add_view_url = self.get_add_view_url(request, memo)
        if add_view_url:
            return HttpResponseRedirect(add_view_url)

        return super().response_post_save_change(request, memo)

    def save_model(self, request, obj, form, change):
        if 'stage' in form.changed_data and obj.stage == obj.REVIEWED:
            if "_create-task" in request.POST:
                obj.stage = obj.POSTPONED
            else:
                if not obj.review_date:
                    obj.review_date = self.today
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        if 'stage' in form.changed_data and obj.stage == obj.REVIEWED:
            obj.send_review_notification()

        if not change:
            if obj.deal:
                deal = obj.deal
                message = _("The office memo was written")
                deal.add_to_workflow(f"{message} - {obj.name}")
                deal.save(update_fields=['workflow'])
        if all((
                not obj.draft,
                not obj.notified,
                request.user == obj.owner
        )):
            link = f'<a href="{obj.get_absolute_url()}"> {obj.name}  ({obj.owner})</a>'
            message = _("You've received a office memo")
            save_message(obj.to, f"{message} - {link}")
            subject = compose_subject(obj, message)
            email_to_participants(obj, subject, [obj.to.email])
            obj.notified = True
            obj.save(update_fields=['notified'])

        if not obj.draft and obj.subscribers.exists():
            if "subscribers" in form.changed_data or 'draft' in form.changed_data:
                notified = obj.notified_subscribers.all()
                difference = obj.subscribers.exclude(id__in=notified)
                if difference:
                    recipient_list, notified = [], []
                    subject = compose_subject(obj, subscribers_subject)
                    msg = (subject
                           + f'<a href="{obj.get_absolute_url()}"> {obj.name}  ({obj.owner})</a>')
                    for user in difference:
                        save_message(user, msg, "INFO")
                        if getattr(user, "email"):
                            recipient_list.append(user.email)
                            notified.append(user)
                        else:
                            notify_admins_no_email(user)
                    if recipient_list:
                        email_to_participants(obj, subject, recipient_list)
                    if notified:
                        obj.notified_subscribers.add(*notified)

    # -- ModelAdmin callables -- #

    @admin.display(description='')
    def action(self, obj):
        if obj.task:
            url = obj.task.get_absolute_url()
            value = _('View the task')
            instance = obj.task
        elif obj.project:
            url = obj.project.get_absolute_url()
            value = _('View the project')
            instance = obj.project
        else:
            return ''
        style, mouseover, mouseout, title = self.get_style(instance)
        li = f'<li><a style="{style}" href="{url}" title="{title}"' \
             f'onMouseOver="{mouseover}" onMouseOut="{mouseout}">{value}</a></li>'
        return mark_safe(
            '<ul class="object-tools" style="margin-top:0px;'
            f'margin-left:-10px;white-space:nowrap;">{li}</ul>'
        )

    @admin.display(description='')
    def content_copy(self, obj):
        url = reverse("site:tasks_memo_add") + f"?copy_memo={obj.id}"
        return mark_safe(CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))

    @staticmethod
    @admin.display(description=mark_safe(
        event_available_icon.format(get_verbose_name(Memo, "review_date"))
    ))
    def date_of_review(obj):
        if obj.review_date:
            return mark_safe(
                '<div title="{}">{}</div>'.format(
                    get_verbose_name(Memo, "review_date"),
                    date_format(obj.review_date, format="SHORT_DATE_FORMAT", use_l10n=True)
                )
            )
        return ''

    @admin.display(description=department_str)
    def department(self, obj):
        value = LEADERS
        if getattr(obj, "department", None):
            value = getattr(obj, "department")
        return mark_safe(
            f'<div title="{department_str}">{value}</div>'
        )

    @admin.display(description=status_str)
    def status(self, obj):
        if obj.stage == obj.REVIEWED:
            return mark_safe(
                f'<i class="material-icons" title="{_("Status")}: {reviewed_str}"'
                ' style="color: var(--green-fg)">assignment_turned_in</i>'
            )
        if obj.stage == obj.POSTPONED:
            return mark_safe(
                f'<i class="material-icons" title="{_("Status")}: {postponed_str}"'
                ' style="color: var(--green-fg)">low_priority</i>'
            )
        if obj.draft:
            return mark_safe(
                f'<i class="material-icons" title="{_("Status")}: {draft_str}"'
                ' style="color: var(--error-fg)">visibility_off</i>'
            )

        else:
            return mark_safe(
                f'<i class="material-icons" title="{_("Status")}: {unreviewed_str}"'
                ' style="color: var(--error-fg)">assignment_late</i>'
            )

    @admin.display(description=_("subscribers"))
    def subscribers_list(self, obj):
        return mark_safe(
            f'<b>{", ".join([str(u) for u in obj.subscribers.all()])}</b>'
        )

    @admin.display(description='')
    def view_button(self, obj):
        li = ''
        for attr in ('task', 'project', 'deal'):
            obj = getattr(obj, attr, None)
            if obj:
                url = obj.get_absolute_url()
                title = _("View the " + attr)
                li += f'<li><a href="{url}" target="_blank">{title}</a></li>'
        return mark_safe(
            f'<ul class="object-tools" style=" margin-left: -170px;margin-top: 0px;">{li}</ul>'
        )

    # -- Custom methods -- #

    @staticmethod
    def get_add_view_url(request: WSGIRequest, memo: Memo) -> tuple:
        """
        Returns the add_view url for the Task or Project
        with relevant query string
        """
        add_view_url = ''

        if '_create-task' in request.POST:
            if memo.task:
                add_view_url = reverse("site:tasks_task_change", args=(memo.task.id,))
            else:
                add_view_url = reverse("site:tasks_task_add")

        elif '_create-project' in request.POST:
            if memo.project:
                add_view_url = reverse("site:tasks_project_change", args=(memo.project.id,))
            else:
                add_view_url = reverse("site:tasks_project_add")

        if add_view_url:
            params = {
                'parent_memo_id': memo.id,
                'next_url': reverse("site:tasks_memo_changelist")
            }
            add_view_url = add_view_url + f"?{urlencode(params)}"

        return add_view_url

    def get_style(self, obj) -> tuple:
        stage = obj.stage
        stage_data = (stage.default, stage.active, stage.done, stage.in_progress)
        title = _(stage.name)
        if obj.due_date:
            if stage_data in ((True, True, False, False), (False, True, False, True)):
                if obj.due_date < self.today:
                    stage_data = 'overdue'
                    title = f"{title}, {overdue_str}"
        col1, col2 = style_data[stage_data]
        style = f"background-color: {col1};"
        mouseover = f"this.style.background='{col2}'"
        mouseout = f"this.style.background='{col1}'"
        return style, mouseover, mouseout, title


style_data = {
    (True, True, False, False): ('#ECBA82', '#7D4F50'),             # pending
    (False, True, False, True): ('var(--green-fg)', '#173F16FF'),   # In progress
    (False, False, True, False): ('var(--close-button-bg)',
                                  'var(--close-button-hover-bg)'),  # done
    (False, True, False, False): ('#A390E4', '#4B296B'),            # postponed
    (False, False, False, False): ('var(--body-loud-color)',
                                   'var(--body-quiet-color)'),      # canceled
    'overdue': ('var(--delete-button-bg)', 'var(--delete-button-hover-bg)')
}
