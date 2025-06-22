from urllib.parse import urlencode
from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Case
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Least
from django.http import HttpResponseRedirect
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.utils.safestring import mark_safe

from common.utils.helpers import add_chat_context
from common.utils.helpers import set_toggle_tooltip
from common.utils.helpers import CONTENT_COPY_ICON
from common.utils.helpers import CONTENT_COPY_LINK
from common.utils.helpers import COPY_STR
from common.utils.helpers import annotate_chat
from common.utils.helpers import get_active_users
from common.utils.helpers import get_delta_date
from common.utils.helpers import get_today
from tasks.models import Task
from tasks.models import TaskStage
from tasks.forms import TaskForm
from tasks.site.tasksbasemodeladmin import notify_task_or_project_closed
from tasks.site.tasksbasemodeladmin import TASK_NEXT_STEP
from tasks.site.tasksbasemodeladmin import TasksBaseModelAdmin
from tasks.utils.admfilters import ByProject

COMPLETED_TITLE = gettext_lazy("I completed my part of the task")
task_was_created_str = _("The task was created")
subtask_was_created_str = _("The subtask was created")
the_subtask_str = _("The subtask")


class TaskAdmin(TasksBaseModelAdmin):

    actions = ['export_selected']
    empty_value_display = ''
    filter_horizontal = ('responsible', 'subscribers')
    form = TaskForm
    list_display = (
        'coloured_name', 'next_step', 'coloured_next_step_date',
        'priority_field', 'stage', 'chat_link', 'responsible_list', 'act',
        'coloured_due_date', 'created',     # 'lead_time_field',
        'id', 'person', 'content_copy'
    )
    radio_fields = {'stage': admin.HORIZONTAL}
    raw_id_fields = ('project', 'task')

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        set_toggle_tooltip("task_step_date_sorting", request, extra_context)
        next_url = request.get_full_path()
        url = reverse("toggle_default_sorting")
        extra_context['toggle_sorting_url'] = f"{url}?model=Task&next_url={next_url}"
        return super().changelist_view(request, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        url = self.get_url_if_no_object(request, object_id)
        if url:
            return HttpResponseRedirect(url)
        extra_context = extra_context or {}
        extra_context['subtask_num'] = Task.objects.filter(
            task_id=object_id).count()
        content_type = ContentType.objects.get_for_model(Task)
        extra_context['content_type_id'] = content_type.id
        add_chat_context(request, extra_context, object_id, content_type)
        self.add_remainder_context(
            request, extra_context, object_id, content_type)

        task = Task.objects.get(id=object_id)
        extra_context['show_completed'] = True
        if any((
                extra_context['subtask_num'],
                task.responsible.count() > 1,
                task.stage.done
        )):
            extra_context['show_completed'] = False
            if request.user in task.responsible.all():
                extra_context['add_subtask_url'] = self.get_add_subtask_url(object_id)
        if any((
                request.user.is_chief,
                request.user.is_department_head,
                request.user.is_task_operator,
        )):
            extra_context['show_create_project'] = True
        url = reverse("site:tasks_task_add") + f"?copy_task={object_id}"
        extra_context['content_copy_link'] = mark_safe(
            CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))
        return super().change_view(
            request, object_id, form_url,
            extra_context=extra_context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "task":
            parent_task_id = request.GET.get("parent_task_id")
            if parent_task_id:
                kwargs["initial"] = parent_task_id

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "responsible":
            users = get_active_users()
            responsible = users

            if not any((request.user.is_chief, request.user.is_superuser,
                        request.user.is_task_operator)):
                department_users = None
                if request.user.is_department_head:
                    if request.user.is_accountant:
                        department_id = request.user.groups.get(
                            name='Bookkeeping'
                        ).id
                    else:
                        department_id = request.user.department_id
                    department_users = users.filter(
                        groups=department_id
                    )
                    responsible = department_users
                else:
                    responsible = users.filter(id=request.user.id)
                    kwargs["initial"] = responsible

                task_id = request.resolver_match.kwargs.get('object_id')
                if task_id:  # object exists
                    task = Task.objects.get(id=task_id)
                    if getattr(task, "task", None):  # task is subtask
                        responsible = task.task.responsible.all()
                        if department_users:
                            responsible = users.filter(
                                Q(id__in=responsible) | Q(id__in=department_users)
                            )
                        else:
                            responsible = users.filter(
                                Q(id__in=responsible) | Q(id=request.user.id)
                            )
                else:  # object does not exist
                    parent_task_id = request.GET.get("parent_task_id")
                    if parent_task_id:  # task is subtask
                        parent_task = Task.objects.get(id=parent_task_id)
                        responsible = parent_task.responsible.all()
                    if department_users:
                        responsible = users.filter(
                            Q(id__in=responsible) | Q(id__in=department_users)
                        )
            kwargs["queryset"] = responsible.order_by("username")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        # for use in the admin add and change views
        initial = super().get_changeform_initial_data(request)
        initial['next_step'] = TASK_NEXT_STEP
        initial['next_step_date'] = get_delta_date(1)
        initial['stage'] = TaskStage.objects.filter(default=True).first()
        task_id = request.GET.get('copy_task')
        if task_id:
            task = Task.objects.prefetch_related(
                'responsible', 'subscribers', 'tags'
            ).get(id=task_id)
            initial['name'] = task.name
            initial['description'] = task.description
            initial['task'] = task.task
            initial['project'] = task.project
            initial['note'] = task.note
            initial['priority'] = task.priority
            initial['co_owner'] = task.co_owner
            initial['responsible'] = task.responsible.all()
            initial['subscribers'] = task.subscribers.all()
            initial['tags'] = task.tags.all()
        return initial

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        if cl.result_list:
            cl.result_list = annotate_chat(request, cl.result_list)
        return cl
    
    def get_list_filter(self, request, obj=None):
        list_filter = super().get_list_filter(request, obj)
        list_filter.append(ByProject)
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        active = request.GET.get('active')
        if active is None and "task_step_date_sorting" in request.session:
            qs = qs.annotate(
                step_date=Coalesce("task__next_step_date", "next_step_date"),
                parent_id=Coalesce("task_id", "id"),
            )
            queryset = qs.order_by("step_date", "parent_id", "id")
        else:
            qs = qs.annotate(
                step_date=Least(
                    Coalesce("task__next_step_date", "next_step_date"),
                    "next_step_date"
                ),
                parent_task=Case(
                    When(task__isnull=True, then=Value(0)),
                    default=Value(1)
                ),
                parent_id=Coalesce("task_id", "id"),
            )
            queryset = qs.order_by("-parent_id", "parent_task", "step_date", "id")
        return queryset

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields.extend(["lead_time_field", "content_copy"])
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        main_task_changed = False
        main_task = obj.task

        if not change:
            msg = task_was_created_str
            if main_task:
                msg = subtask_was_created_str
                obj.co_owner = main_task.task.owner if main_task.task else main_task.owner
                if request.user in form.cleaned_data['responsible']:
                    if obj.stage.active:
                        obj.stage = TaskStage.objects.filter(in_progress=True).first()
            obj.add_to_workflow(f'{msg}. ({request.user})')
        
        if main_task:
            if main_task.due_date:
                field = ""
                if obj.next_step_date and obj.next_step_date > main_task.due_date:
                    field = obj._meta.get_field("next_step_date").verbose_name  # NOQA

                if obj.due_date and obj.due_date > main_task.due_date:
                    field = obj._meta.get_field("due_date").verbose_name  # NOQA
                if field:
                    model_name = obj._meta.verbose_name  # NOQA
                    link = f'{model_name} \
                    <a href="{obj.get_absolute_url()}">"{obj.name}".</a>'
                    description = _("later than due date of parent task.")
                    messages.warning(
                        request, mark_safe(f'{link} "{field}" {description}')
                    )

        if "next_step" in form.changed_data:
            if main_task:
                main_task.add_to_workflow(f'{obj.next_step}. ({request.user})')
                main_task_changed = True
                if main_task.next_step == TASK_NEXT_STEP and obj.next_step != TASK_NEXT_STEP \
                        or main_task.next_step_date > obj.next_step_date:  # it's right
                    main_task.next_step = obj.next_step
                    main_task.next_step_date = obj.next_step_date
        elif not obj.next_step:
            obj.next_step = TASK_NEXT_STEP

        if '_completed' in request.POST:
            obj.stage = TaskStage.objects.filter(done=True).first()
            obj.closing_date = get_today()
            self.update_next_step_and_workflow(request, obj, form)

        if "stage" in form.changed_data:
            if not obj.stage.active:
                obj.closing_date = get_today()
            self.update_next_step_and_workflow(request, obj, form)

        elif not getattr(obj, 'stage', None):
            obj.stage = TaskStage.objects.filter(default=True).first()

        super().save_model(request, obj, form, change)
        if main_task_changed:
            main_task.save()
        if not change and request.GET.get("parent_project_id"):
            obj.project_id = request.GET.get("parent_project_id")
            obj.project.add_to_workflow(f'{task_was_created_str} ({request.user})')
            obj.project.save()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        main_task = obj.task
        main_task_update_fields = []
        if main_task:
            if not change:
                main_task.add_to_workflow(
                    f"{subtask_was_created_str}: {obj.name} ({request.user})")
                main_task_update_fields.append('workflow')

            if main_task.stage.default and obj.stage.in_progress \
                    or not main_task.stage.active and obj.stage.active:
                main_task.stage_id = TaskStage.objects.filter(
                    in_progress=True
                ).first().id
                main_task_update_fields.append('stage')

            if '_completed' in request.POST or "stage" in form.changed_data:
                if "next_step" not in form.changed_data \
                        or obj.next_step == TASK_NEXT_STEP:
                    main_task.add_to_workflow(
                        f"{obj.next_step}. {the_subtask_str}: {obj.name} ({request.user})")
                    main_task_update_fields.append('workflow')
            main_task.save(update_fields=main_task_update_fields)

        if (
            "stage" in form.changed_data
            and not obj.active
            or "_completed" in request.POST
        ):
            if main_task:
                obj.check_and_deacte_main_task()
                obj.copy_files_to_maintask()
                if not main_task.active:
                    notify_task_or_project_closed(request, main_task)

        # make a file attached to a closed subtask available in the main task
        if main_task and all((not obj.active,
                              "stage" not in form.changed_data,
                              "_completed" not in request.POST)):
            obj.copy_files_to_maintask()

    # -- ModelAdmin callables -- #

    @admin.display(
        description=mark_safe(
            '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
        ),
        ordering='name'
    )
    def coloured_name(self, obj):
        if not obj.task:
            return mark_safe(
                '<span style="color: var(--green-fg)" title="{title}">{name}</span>'.format(
                    title=_("Main task"),
                    name=obj.name
                ))
        return mark_safe(f'<span style="margin-left:20px; display:block;">{obj.name}</span>')

    @admin.display(description='')
    def content_copy(self, obj):
        url = reverse("site:tasks_task_add") + f"?copy_task={obj.id}"
        return mark_safe(CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))
    
    @admin.display(
        description=mark_safe(
            '<div title="{}">{}</div>'.format(_("Lead time"), '<i class="material-icons">hourglass_empty</i>')
        ),
        ordering="lead_time"
    )
    def lead_time_field(self, obj):
        return mark_safe(
            '<div title="{}">{}</div>'.format(_("Lead time"), obj.lead_time)
        )

    @admin.display(
        description=mark_safe(
            '<i class="material-icons" style="color: var(--orange-fg)">info_outline</i>'
        ))
    def notice(self, obj):
        subtask_url = self.get_add_subtask_url(obj.id)
        subtask_title = _("Create subtask")
        subtask_button_name = _('Create subtask')
        completed_url = reverse(
            "create_completed_subtask", args=(obj.id,))
        completed_button_name = _('Completed')
        li = f'<li><a title="{subtask_title}" href="{subtask_url}">' \
             f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">assignment</i>' \
             f' {subtask_button_name}</a></li>' \
             f'<li><a title="{COMPLETED_TITLE}" href="{completed_url}">' \
             f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">assignment_turned_in</i>' \
             f' {completed_button_name}</a></li>'
        msg = _("""This is a collective task.
            Please create a sub-task for yourself for work.
            Or press the next button when you have done your job.
        """)
        button = f'<ul class="object-tools" style=" margin-left: 0px;margin-top: 0px">{li}</ul>'
        html_msg = linebreaks(f'<span style="color: var(--orange-fg)">{msg}</span>')
        return mark_safe(f"{html_msg}{button}")

    @staticmethod
    def step_date(obj):
        return obj.step_date

    @staticmethod
    def parent_id(obj):
        return obj.parent_id

    # -- Custom methods -- #

    @staticmethod
    def get_add_subtask_url(object_id: int) -> str:
        add_view_url = reverse("site:tasks_task_add")
        params = {
            "parent_task_id": object_id,
            "next_url": reverse("site:tasks_task_changelist")
        }
        add_view_url = add_view_url + f"?{urlencode(params)}"
        return add_view_url
    
    @staticmethod
    def update_next_step_and_workflow(request: WSGIRequest,
                                      obj: Task, form: TaskForm) -> None:
        if "next_step" not in form.changed_data \
                or obj.next_step == TASK_NEXT_STEP:
            
            field_name = ''
            if obj.stage.in_progress:
                field_name = 'in_progress'            
            elif obj.stage.done:
                field_name = 'done'
            
            if field_name:
                obj.next_step = obj.stage._meta.get_field(   # NOQA
                    field_name
                ).verbose_name
            else:
                obj.next_step = _(obj.stage.name)
            
            obj.add_to_workflow(f'{obj.next_step}. ({request.user})')
