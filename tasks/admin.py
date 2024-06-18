from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from common.utils.for_translation import check_for_translation
from crm.site.crmadminsite import crm_site
from tasks.models import Memo
from tasks.models import Resolution
from tasks.models import Project
from tasks.models import ProjectStage
from tasks.models import Tag
from tasks.models import Task
from tasks.models import TaskStage
from tasks.site import memoadmin
from tasks.site import projectadmin
from tasks.site import taskadmin
from tasks.site.tagadmin import TagAdmin


class TranslateNameModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        check_for_translation(request, obj, form)


class MemoAdmin(memoadmin.MemoAdmin):
    readonly_fields = [
        'name_icon',
        'creation_date',
        'modified_by',
        'status',
        'action',
        'date_of_review',
        'view_button',
        'update_date'
    ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[0][1]['fields'].insert(2, 'update_date')
        return fieldsets


class ProjectAdmin(projectadmin.ProjectAdmin):

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': (
                    'name',
                    ('due_date', 'priority'),
                    'description',
                    'note',
                    'stage',
                    'next_step',
                    'next_step_date',
                    'workflow_area',
                    ('creation_date', 'closing_date'),
                    ('owner', 'co_owner'),
                    'responsible_list'
                )
            }),
            (_('Change responsible'), {
                'classes': ('collapse',),
                'fields': ('responsible',)
            }),
            (None, {
                'fields': ('subscribers_list',)
            }),
            (_('Change subscribers'), {
                'classes': ('collapse',),
                'fields': ('subscribers',)
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    'start_date', 'closing_date',
                    'active'
                )
            }),
        ]
        fieldsets.extend(self.get_tag_fieldsets(obj))
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=None)
        readonly_fields.remove('owner')
        return readonly_fields


class ResolutionAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'index_number')


class TaskAdmin(taskadmin.TaskAdmin):

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': (
                    'name',
                    ('due_date', 'priority'),
                    'description',
                    'note',
                    ('stage', 'hide_main_task'),
                    'next_step',
                    'next_step_date',
                    'workflow_area',
                    ('creation_date', 'closing_date'),
                    ('owner', 'co_owner'),
                    'responsible_list'
                )
            }),
            (_('Change responsible'), {
                'classes': ('collapse',),
                'fields': ('responsible',)
            }),
            (None, {
                'fields': ('subscribers_list',)
            }),
            (_('Change subscribers'), {
                'classes': ('collapse',),
                'fields': ('subscribers',)
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    'task', 'project', 'hide_main_task',
                    'start_date', 'closing_date',
                    'active',
                    'token'
                )
            }),
        ]
        fieldsets.extend(self.get_tag_fieldsets(obj))
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=None)
        readonly_fields.remove('owner')
        readonly_fields.append('token')
        return readonly_fields


class TaskStageAdmin(TranslateNameModelAdmin):
    list_display = (
        'name', 'default',
        'active', 'done',
        'in_progress',
        'index_number'
    )
    fields = (
        'name', 'default',
        'active', 'done',
        'in_progress',
        'index_number'
    )


class ProjectStageAdmin(TranslateNameModelAdmin):
    list_display = (
        'name', 'default',
        'active', 'done',
        'in_progress',
        'index_number'
    )
    fields = (
        'name', 'default',
        'active', 'done',
        'in_progress',
        'index_number'
    )


admin.site.register(Memo, MemoAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TaskStage, TaskStageAdmin)
admin.site.register(Resolution, ResolutionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(ProjectStage, ProjectStageAdmin)

crm_site.register(Memo, memoadmin.MemoAdmin)
crm_site.register(Project, projectadmin.ProjectAdmin)
crm_site.register(Resolution, ResolutionAdmin)
crm_site.register(Tag, TagAdmin)
crm_site.register(Task, taskadmin.TaskAdmin)
