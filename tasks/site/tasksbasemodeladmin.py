import os
from typing import Union
from urllib.parse import urlencode
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import OuterRef
from django.http import HttpResponseRedirect
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.admin import FileInline
from common.models import TheFile
from common.site.basemodeladmin import BaseModelAdmin
from common.utils.email_to_participants import email_to_participants
from common.utils.helpers import compose_subject
from common.utils.helpers import CRM_NOTICE
from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_active_users
from common.utils.helpers import get_department_id
from common.utils.helpers import get_today
from common.utils.helpers import get_formatted_short_date
from common.utils.helpers import LEADERS
from common.utils.helpers import notify_admins_no_email
from common.utils.notify_user import notify_user
from common.utils.helpers import save_message
from common.utils.remind_me import remind_me
from tasks.models import Memo
from tasks.models import Project
from tasks.models import Task
from tasks.utils.admfilters import ByResponsibleFilter
from tasks.utils.admfilters import IsActiveTaskFilter
from tasks.utils.admfilters import ByOwnerFilter
from tasks.utils.admfilters import TaskTagFilter

chat_icon = '<i class="material-icons" style="font-size: 17px;color: var(--body-quiet-color)">forum</i>'
chat_red_icon = '<i class="material-icons" style="font-size: 17px;color: var(--error-fg)">forum</i>'
chat_link_str = '<a href="{}?content_type__id={}&object_id={}" title="{}" target="_blank">{}</a>'
co_owner_subject = _("You have been assigned as the task co-owner")
due_date_str = _("Due date")
TASK_NEXT_STEP = _("Acquainted with the task")
NEXT_STEP_DATE_WARNING = _("The next step date should not be later than due date.")
subscribers_subject = _("You are subscribed to a new task")
responsible_subject = _("You have a new task assigned")
priority_icon = '<i class="material-icons">flash_on</i>'
priority_style_icon = '<i class="material-icons" style="font-size: 17px;color:{}">{}</i>'
view_chat_str = _("View chat messages")


class TasksBaseModelAdmin(BaseModelAdmin):
    inlines = [FileInline]
    list_per_page = 50
    search_fields = ("name", "description", "workflow")

    # -- ModelAdmin methods -- #

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stage":
            kwargs["empty_label"] = None

        if db_field.name == "co_owner":
            if not request.resolver_match.kwargs.get('object_id'):
                users = get_active_users()
                if not any((
                        request.user.is_chief,
                        request.user.is_task_operator
                )):
                    group_names = request.user.groups.values_list(
                        "name", flat=True)
                    if "department heads" in group_names:
                        chiefs = users.filter(
                            groups__name="chiefs"
                        ).order_by("username")
                        kwargs["queryset"] = chiefs
                    else:  # user is not department head
                        department_heads = users.filter(
                            groups=request.user.department_id
                        ).filter(groups__name="department heads")
                        kwargs["queryset"] = department_heads
                        kwargs["initial"] = department_heads.first()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "subscribers":
            kwargs["queryset"] = get_active_users().order_by("username")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        parent_obj = None
        initial = super().get_changeform_initial_data(request)
        parent_memo_id = request.GET.get("parent_memo_id")
        parent_task_id = request.GET.get("parent_task_id")
        parent_project_id = request.GET.get("parent_project_id")
        if parent_memo_id:
            parent_obj = Memo.objects.get(id=parent_memo_id)
            initial["subscribers"] = [parent_obj.owner.id]
        elif parent_task_id:
            parent_obj = Task.objects.get(id=parent_task_id)
            subscribers = parent_obj.responsible.exclude(
                Q(id=request.user.id) | Q(is_active=False)
            )
            if subscribers:
                initial["subscribers"] = subscribers
        elif parent_project_id:
            parent_obj = Project.objects.get(id=parent_project_id)
        if parent_obj:
            initial["name"] = parent_obj.name
            initial["description"] = f"{parent_obj.description}\n({parent_obj.owner})"
            initial["note"] = parent_obj.note
        return initial

    def get_fieldsets(self, request, obj=None):
        if obj:
            responsible = obj.responsible.all()
            if self.has_change_permission(request, obj):
                fieldsets = []
                fields = []
                if len(responsible) > 1 and obj.__class__ == Task:
                    if request.user in responsible:
                        fields.append("notice")
                fields.extend([
                    "name",
                    ("due_date", "priority"),
                    "description",
                    "note"
                ])
                if (
                        getattr(obj, "task", None)
                        and obj.task.responsible.count() > 1
                        and request.user in obj.task.responsible.all()
                ):
                    fields.append("stage")
                    fields.append("hide_main_task")
                else:
                    fields.append("stage")
                if len(responsible) == 1 or request.user in (obj.owner, obj.co_owner):
                    fields.extend(["next_step", ("next_step_date", "remind_me")])
                fields.extend([
                    "workflow_area",
                    ("creation_date", "closing_date"),
                    ("owner", "co_owner"),
                ])
                if obj.__class__ == Task and obj.responsible.count() == 1:
                    fields.append("lead_time")
                if responsible:
                    fields.append("responsible_list")
                fieldsets.append((None, {"fields": fields}))
                if request.user in (obj.owner, obj.co_owner) or any(
                        (request.user.is_task_operator, request.user.is_superuser)
                ):
                    fieldset = (_("Change responsible"), {"fields": ("responsible",)})
                    if responsible:
                        fieldset[1]["classes"] = ("collapse",)
                    fieldsets.append(fieldset)
                if obj.subscribers.exists():
                    fieldsets.append(
                        (None, {"fields": ("subscribers_list",)}),
                    )
                fieldsets.append((_("Change subscribers"), {
                    "classes": ("collapse",), "fields": ("subscribers",)
                }))
                fieldsets.extend(self.get_tag_fieldsets(obj))
            else:  # user has no change permission
                fieldsets = [(None, {
                    "fields": [
                        "name",
                        ("due_date", "priority"),
                        "description",
                        "note",
                        'stage',
                        "workflow_area",
                        ("creation_date", "closing_date"),
                        ("owner", "co_owner"),
                    ]
                })]
                if self.model == Task:
                    fieldsets[0][1]["fields"].insert(-1, "lead_time")
                if responsible:
                    fieldsets[0][1]["fields"].append("responsible_list")
                if request.user in responsible and obj.__class__ == Task:
                    fieldsets[0][1]["fields"].insert(0, "notice")
                if obj.subscribers.exists():
                    fieldsets[0][1]["fields"].append("subscribers_list")
        else:  # obj = None
            fields = [
                "name",
                ("due_date", "priority"),
                "description",
                "note",
                "responsible",
                ("owner", "co_owner"),
                'token'
            ]
            if self.model == Task and request.GET.get("parent_task_id"):
                fields.insert(0, "please_edit")
                fields.append('task')
                fields.extend(('stage', "hide_main_task"))
            fieldsets = [
                (None, {"fields": fields}),
                (_("Change subscribers"), {
                    "classes": ("collapse",),
                    "fields": ("subscribers",)
                }),
                (_("Add tags"), {
                    "classes": ("collapse",),
                    "fields": ("tags",)
                })
            ]
            fieldsets = self.attach_file_fields(request, fieldsets)
        if self.model == Task:
            fieldsets.append((_('Additional information'), {
                'classes': ('collapse',),
                'fields': ['project']
            }))
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.parent_memo_id = request.GET.get('parent_memo_id')
            form.parent_task_id = request.GET.get('parent_task_id')
            form.parent_project_id = request.GET.get('parent_project_id')
        return form

    def get_list_filter(self, request, obj=None):
        list_filter = [
            ByOwnerFilter,
            ByResponsibleFilter,
            IsActiveTaskFilter,
            TaskTagFilter,
            "creation_date",
        ]
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if any((
                request.user.is_superuser,
                request.user.is_chief,
                request.user.is_task_operator
        )):
            return qs

        q_params = Q(co_owner=request.user)
        q_params |= Q(owner=request.user)
        q_params |= Q(responsible=request.user)
        q_params |= Q(subscribers=request.user)
        if self.model == Task:
            q_params |= Q(task__subscribers=request.user)
        if any((
                request.GET.get("task__id__exact"),
                request.GET.get("_changelist_filters")
        )):
            if self.model.__class__ == Task:
                q_params |= Q(task__responsible=request.user)
                if request.user.is_department_head:
                    department_id = get_department_id(request.user)
                    department_users = USER_MODEL.objects.filter(
                        groups=department_id)
                    q_params |= Q(responsible__in=department_users)
                    q_params |= Q(task__responsible__in=department_users)
        else:
            q_params |= Q(owner=request.user)

        return qs.filter(q_params).distinct()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "creation_date",
            "workflow",
            "modified_by",
            "act",
            "responsible_list",
            "subscribers_list",
            "coloured_name",
            "closing_date",
            "tag_list",
            "workflow_area",
            "parent_id",
            "notice",
            "owner",
            "please_edit",
            "chat_link"
        ]
        if obj:
            if request.user not in (obj.owner, obj.co_owner) and not any(
                    (request.user.is_task_operator, request.user.is_superuser)
            ):
                readonly_fields.extend(["co_owner", "responsible"])

        return readonly_fields

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if value is False or not obj:
            return value

        if request.user in (obj.owner, obj.co_owner) or any((
                request.user.is_chief,
                request.user.is_task_operator,
                request.user.is_superuser)):
            return True

        if obj.responsible.count() == 1 and request.user == obj.responsible.first():
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        value = super().has_delete_permission(request, obj)
        if value is False or not obj:
            return value

        if request.user in (obj.owner, obj.co_owner) or any((
                request.user.is_chief,
                request.user.is_task_operator,
                request.user.is_superuser)):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        value = super().has_view_permission(request, obj)
        if value is False or not obj:
            return value

        if request.user in (obj.owner, obj.co_owner) or any((
                request.user.is_chief,
                request.user.is_task_operator,
                request.user.is_superuser,
        )):
            return True

        if obj.__class__ == Task:
            # Task participants can see sub-tasks
            # of other participants.
            # A subscriber to the main task can also see all subtasks.
            if obj.task:
                tasks = self.model.objects.filter(
                    Q(id=obj.id) | Q(task=obj) | Q(id=obj.task.id)
                )
            else:
                tasks = self.model.objects.filter(Q(id=obj.id) | Q(task=obj))
            return tasks.filter(
                Q(responsible=request.user) | Q(subscribers=request.user)
            ).exists()
        # obj is Project
        return (
            self.model.objects.filter(Q(id=obj.id))
            .filter(Q(responsible=request.user) | Q(subscribers=request.user))
            .exists()
        )

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            next_url = request.GET.get("next_url")
            if next_url and post_url_continue is None:
                absolute_url = obj.get_absolute_url()
                post_url_continue = absolute_url + f"?next_url={next_url}"
        return super().response_add(request, obj, post_url_continue)

    def response_post_save_add(self, request, obj):
        next_url = request.GET.get("next_url")
        if next_url:
            return HttpResponseRedirect(next_url)
        add_view_url = self.get_add_view_url(request, obj)
        if add_view_url:
            return HttpResponseRedirect(add_view_url)
        return super().response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        add_view_url = self.get_add_view_url(request, obj)
        if add_view_url:
            return HttpResponseRedirect(add_view_url)
        next_url = request.GET.get("next_url")
        if next_url:
            return HttpResponseRedirect(next_url)
        return super().response_post_save_change(request, obj)

    def save_model(self, request, obj, form, change):
        if "next_step" in form.changed_data:
            if obj.responsible.count() == 1 and obj.responsible.get() != request.user:
                obj.next_step += f" ({request.user})"
            obj.add_to_workflow(f'{obj.next_step}.')

        if "next_step_date" in form.changed_data:
            if (
                    all((obj.next_step_date, obj.due_date))
                    and obj.next_step_date > obj.due_date
            ):
                html_msg = (
                        NEXT_STEP_DATE_WARNING
                        + f'<a href="{obj.get_absolute_url()}"> {obj.name}  ({obj.owner})</a>'
                )
                save_message(request.user, html_msg, "INFO")

        super().save_model(request, obj, form, change)
        
        if not change and getattr(obj, 'task', None):
            obj.subscribers.remove(obj.responsible.first())        

        if hasattr(obj, "attach_files"):
            for f in obj.attach_files:
                TheFile.objects.create(file=f.file, content_object=obj)

        parent_memo_id = request.GET.get('parent_memo_id')
        if parent_memo_id:
            memo = Memo.objects.get(id=parent_memo_id)
            if memo.stage != memo.REVIEWED:
                memo.stage = memo.REVIEWED
                if obj.__class__ == Task:
                    memo.task = obj
                    msg = _("The task was created")
                else:
                    memo.project = obj
                    msg = _("The Project was created")
                date = get_formatted_short_date()
                memo.note = f"{date} - {msg}\n\n" + obj.note
                memo.review_date = get_today()
                memo.save()
                memo.send_review_notification()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj_modified = False
        if "responsible" in form.changed_data:
            obj_modified = notify_participants(obj, "responsible")
        if "subscribers" in form.changed_data:
            obj_modified = notify_participants(obj, "subscribers") or obj_modified
        if obj_modified:
            obj.save()
        if not change and obj.co_owner:
            notify_co_owner(obj)
        if (
                "stage" in form.changed_data
                and not obj.active
                or "_completed" in request.POST
        ):
            notify_task_or_project_closed(request, obj)
        remind_me(request, form, change)

    # -- ModelAdmin callables -- #

    @admin.display(description='')
    def chat_link(self, obj):
        value = ''
        content_type = ContentType.objects.get_for_model(self.model)
        url = reverse('site:chat_chatmessage_changelist')
        if getattr(obj, 'is_chat'):
            value = mark_safe(chat_link_str.format(
                url, content_type.id, obj.id, view_chat_str, chat_icon))
        if getattr(obj, 'is_unread_chat'):
            value = mark_safe(chat_link_str.format(
                url, content_type.id, obj.id, view_chat_str, chat_red_icon))
        return value

    @admin.display(description=mark_safe(
        f'<i class="material-icons" title="{due_date_str}"'
        f' style="color: var(--body-quiet-color)">event_available</i>'
    ))
    def coloured_due_date(self, obj):
        if not obj.due_date:
            return mark_safe(f'<div title="{due_date_str}">{LEADERS}</div>')
        due_date = date_format(
            obj.due_date, format="SHORT_DATE_FORMAT", use_l10n=True
        )
        if not obj.active:
            return mark_safe(f'<div title="{due_date_str}">{due_date}</div>')
        color = "gray"
        if obj.due_date < get_today():
            color = "var(--error-fg)"
        return mark_safe(
            f'<div title="{due_date_str}" style="color:{color};">{due_date}</div>'
        )

    @staticmethod
    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--orange-fg)">info_outline</i>'
    ))
    def please_edit(obj):  # NOQA
        msg = _("Please edit the title and description to make it clear to "
                "other users what part of the overall task will be completed.")
        html_msg = linebreaks(f'<span style="color: var(--orange-fg)">{msg}</span>')
        return mark_safe(html_msg)

    @admin.display(description=mark_safe(
        f'<div title="{_("Priority")}">{priority_icon}</div>'
    ), ordering='priority')
    def priority_field(self, obj):
        data = {
            1: (_("Low"), 'flash_off', '--body-quiet-color'),
            2: (_("Middle"), 'flash_on', 'var(--body-loud-color)'),
            3: (_("High"), 'flash_on', 'var(--error-fg)')
        }
        title = f"{_('Priority')}: {data[obj.priority][0]}"
        star = priority_style_icon.format(data[obj.priority][2], data[obj.priority][1])
        return mark_safe(f'<div title="{title}">{star}</div>')

    @admin.display(description=_("responsible"))
    def responsible_list(self, obj):
        return mark_safe(
            f'<b>{", ".join([str(u) for u in obj.responsible.all()])}</b>'
        )

    @admin.display(description=_("subscribers"))
    def subscribers_list(self, obj):
        return mark_safe(
            f'<b>{", ".join([str(u) for u in obj.subscribers.all()])}</b>'
        )

    # -- Custom methods -- #

    def attach_file_fields(self, request: WSGIRequest, fieldsets: list) -> list:
        """
        Adds boolean fields with file names of Memo that the user
        can attach to a Task or Project created from the Memo.
        """
        parent_obj = None
        self.form.declared_fields = {}
        parent_memo_id = request.GET.get("parent_memo_id")
        parent_task_id = request.GET.get("parent_task_id")
        parent_project_id = request.GET.get("parent_project_id")
        if parent_memo_id:
            parent_obj = Memo.objects.get(id=parent_memo_id)
        elif parent_task_id:
            parent_obj = Task.objects.get(id=parent_task_id)
        elif parent_project_id:
            parent_obj = Project.objects.get(id=parent_project_id)
        if parent_obj:
            files = parent_obj.files.all()
            if files:
                fields = [f.file.path.split(os.sep)[-1] for f in files]
                fieldsets.append((_("Attach files"), {"fields": fields}))
                form_fields = {
                    f.file.path.split(os.sep)[-1]: forms.BooleanField(
                        required=False, initial=True
                    )
                    for f in files
                }
                self.form.declared_fields = form_fields
        return fieldsets

    @staticmethod
    def get_add_view_url(request: WSGIRequest,
                         obj: Union[Task, Project]) -> str:
        """
        Returns the add_view url for the Task or Project
        with relevant query string
        """
        add_view_url = ""
        params = {}
        if "_create-task" in request.POST:
            add_view_url = reverse("site:tasks_task_add")

        elif "_create-project" in request.POST:
            add_view_url = reverse("site:tasks_project_add")

        if add_view_url:
            if obj.__class__ == Task:
                if obj.task:
                    parent_task_id = obj.task.id
                else:
                    parent_task_id = obj.id
                params["parent_task_id"] = parent_task_id
                params["next_url"] = reverse("site:tasks_task_changelist")
            elif obj.__class__ == Project:
                params["parent_project_id"] = obj.id
                params["next_url"] = reverse("site:tasks_project_changelist")
            add_view_url = add_view_url + f"?{urlencode(params)}"

        return add_view_url


def exclude_some_users(obj: Task, qs: QuerySet) -> QuerySet:
    """Exclude users who have checked the 'Hide main task' checkbox."""

    if getattr(obj, 'task', None):
        subtasks = Task.objects.filter(
            task__id=obj.task.id,
            hide_main_task=True
        )
        if subtasks:
            filtered_qs = subtasks.filter(responsible=OuterRef('pk'))
            qs = qs.annotate(
                user=Exists(filtered_qs)
            ).exclude(user=True)
    return qs


def notify_co_owner(obj: Union[Task, Project]) -> None:
    link = f'<a href="{obj.get_absolute_url()}"> {obj.name}  ({obj.owner})</a>'
    msg = f'{CRM_NOTICE} {_(co_owner_subject)}: {link}'
    save_message(obj.co_owner, msg, 'INFO')
    subject = compose_subject(obj, co_owner_subject)
    email_to_participants(obj, subject, [obj.co_owner.email])


def notify_participants(obj: Union[Task, Project], field: str) -> bool:

    obj_modified = False
    users = getattr(obj, field).all()
    notified_field = getattr(obj, "notified_" + field)
    notified = notified_field.all()
    difference = users.exclude(id__in=notified)
    if field == "responsible":
        difference = difference.exclude(id=obj.owner_id)
    removed = notified.exclude(id__in=users)
    if removed:
        notified_field.remove(*removed)
        obj_modified = True
    if difference:
        difference = exclude_some_users(obj, difference)
        recipient_list, notified = [], []
        subject = compose_subject(obj, globals()[field + '_subject'])
        msg = (
            f'{subject}<a href="{obj.get_absolute_url()}"> {obj.name}  ({obj.owner})</a>'
        )
        for user in difference:
            if field == "responsible":
                notify_user(obj, user, subject, responsible=user)
                notified.append(user)
            else:
                save_message(user, msg, "INFO")
                if getattr(user, "email"):
                    recipient_list.append(user.email)
                    notified.append(user)
                else:
                    notify_admins_no_email(user)
        if recipient_list and not field == "responsible":
            email_to_participants(obj, subject, recipient_list)
        if notified:
            notified_field.add(*notified)
            obj_modified = True
    return obj_modified


def notify_task_or_project_closed(request: WSGIRequest, obj: Union[Task, Project]):

    recipient_list = []
    if obj.__class__ == Task:
        if obj.task:
            task_is_closed_str = _("The subtask is closed")
        else:
            task_is_closed_str = _("The task is closed")
    else:
        task_is_closed_str = _("The project is closed")
    subscribers = obj.subscribers.all()
    subscribers = exclude_some_users(obj, subscribers)

    users = list(subscribers)
    if obj.owner and obj.owner != request.user:
        users.append(obj.owner)
    if obj.co_owner and obj.co_owner != request.user:
        users.append(obj.co_owner)
    msg = f'{task_is_closed_str}<a href="{obj.get_absolute_url()}"> {obj.name} ({obj.owner})</a>'
    for u in users:
        save_message(u, msg, "INFO")
        if getattr(u, "email"):
            recipient_list.append(u.email)
        else:
            notify_admins_no_email(u)
    if recipient_list:
        subject = compose_subject(obj, task_is_closed_str)
        email_to_participants(obj, subject, recipient_list)
