from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import add_chat_context
from common.utils.helpers import get_active_users
from common.utils.helpers import get_delta_date
from common.utils.helpers import get_today
from tasks.models import Project
from tasks.models import ProjectStage
from tasks.models import Task
from tasks.forms import ProjectForm
from tasks.site.tasksbasemodeladmin import TasksBaseModelAdmin

PROJECT_NEXT_STEP = 'Acquainted with the project'


class ProjectAdmin(TasksBaseModelAdmin):
    filter_horizontal = ('responsible', 'subscribers')
    form = ProjectForm
    list_display = (
        'name',
        'next_step',
        'coloured_next_step_date',
        'due_date',
        'priority',
        'stage',
        'responsible_list',
        'act',
        'created',
        'id'
    )
    radio_fields = {'stage': admin.HORIZONTAL}

    # -- ModelAdmin methods -- #

    def change_view(self, request, object_id, form_url='', extra_context=None):
        url = self.get_url_if_no_object(request, object_id)
        if url:
            return HttpResponseRedirect(url)
        extra_context = extra_context or {}
        extra_context['task_num'] = Task.objects.filter(
            project_id=object_id).count()
        content_type = ContentType.objects.get_for_model(Project)
        extra_context['content_type_id'] = content_type.id
        add_chat_context(request, extra_context, object_id, content_type)
        self.add_remainder_context(
            request, extra_context, object_id, content_type)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "responsible":
            responsible = get_active_users()
            kwargs["queryset"] = responsible.order_by("username")
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['next_step'] = _(PROJECT_NEXT_STEP)
        initial['next_step_date'] = get_delta_date(1)
        initial['stage'] = ProjectStage.objects.filter(default=True).first()
        return initial

    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'stage', None):
            obj.stage = ProjectStage.objects.filter(default=True).first()
        if not obj.next_step:
            obj.next_step = _(PROJECT_NEXT_STEP)
        if '_completed' in request.POST:
            obj.stage = ProjectStage.objects.filter(done=True).first()
            obj.closing_date = get_today()

        if not change:
            msg = _("The project was created")
            obj.add_to_workflow(f'{msg} ({request.user})')
        super().save_model(request, obj, form, change)
