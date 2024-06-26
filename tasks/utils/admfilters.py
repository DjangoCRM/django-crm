from django.contrib.admin import SimpleListFilter
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import LEADERS
from common.utils.helpers import USER_MODEL
from common.utils.hide_main_tasks import hide_main_tasks
from crm.utils import admfilters
from tasks.models import Project
from tasks.models import Tag
from tasks.models import Task


class ByOwnerFilter(admfilters.ByOwnerFilter):

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        task_id = request.GET.get('task__id__exact')
        project_id = request.GET.get('project__id__exact')
        if task_id:
            qs = qs.filter(task__id__exact=task_id)
        if project_id:
            qs = qs.filter(project__id__exact=project_id)
        if not request.user.is_chief or any((task_id, project_id)):
            owner_lookups = self.get_owner_lookups(qs)
            lookups = [(None, _('All')), *owner_lookups]
        else:
            excluded_qs = qs.exclude(owner=request.user)
            owner_lookups = self.get_owner_lookups(excluded_qs)
            lookups = [('all', _('All')), (None, request.user.username), *owner_lookups]

        if qs.filter(owner=None).exists():
            lookups.append(('IsNull', LEADERS))
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"
        return lookups

    def queryset(self, request, queryset):
        if request.user.is_chief and not self.value() and not any((
                request.GET.get('task__id__exact'),
                request.GET.get('project__id__exact')
        )):
            return self.get_owner_queryset(queryset, request.user)

        if self.value() in (x[1] for x in self.lookup_choices):
            return self.get_owner_queryset(queryset, self.value())

        if self.value() == 'IsNull':
            return queryset.filter(owner=None)

        return queryset


class ByProject(SimpleListFilter):
    title = _('Project')
    parameter_name = 'project'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        projects = Project.objects.filter(
            tasks_task_project_related__in=qs,
            stage__active=True
        ).distinct().values_list('id', 'name').order_by('name')
        return [*projects]

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            queryset = queryset.filter(
                Q(project=value) | Q(task__project=value)
            )
        return queryset


class ByResponsibleFilter(admfilters.ChoicesSimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Responsible')
    parameter_name = 'responsible'

    def lookups(self, request, model_admin):
        task_id = request.GET.get('task__id__exact')
        project_id = request.GET.get('project__id__exact')
        qs = model_admin.get_queryset(request)
        if task_id:
            qs = qs.filter(task__id__exact=task_id)
        if project_id:
            qs = qs.filter(project__id__exact=project_id)
            
        filtered_qs = qs.filter(responsible=OuterRef('pk'))
        responsible = USER_MODEL.objects.annotate(
            user_exists=Exists(filtered_qs)
        ).filter(user_exists=True).order_by('username')
        
        if any((task_id, project_id)):
            lookups = [(None, _('All')), *((x.username, x.username) for x in responsible)]
        else:
            responsible = responsible.exclude(id=request.user.id)
            lookups = [('all', _('All')), (None, request.user.username),
                       *((x.username, x.username) for x in responsible)]
        if qs.filter(responsible=None).exists():
            lookups.append(('IsNull', LEADERS))
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        project_id = request.GET.get('project__id__exact')
        if project_id:
            queryset = queryset.filter(project__id=project_id)
        task_id = request.GET.get('task__id__exact')
        if not value:
            if project_id or task_id:
                return queryset

            username = request.user.username
            if queryset.filter(responsible__username=username).exists():
                return queryset.filter(responsible__username=username)
            return queryset

        if value == 'all':
            return queryset

        if value == 'IsNull':
            return queryset.filter(responsible__isnull=True)

        return queryset.filter(responsible__username=value)


class ByToFilter(admfilters.ChoicesSimpleListFilter):
    title = _('To')
    parameter_name = 'to'

    def lookups(self, request, model_admin):
        lookups = [(None, _('All'))]
        queryset = model_admin.get_queryset(request)
        users = USER_MODEL.objects.all()
        if any((
                request.user.is_chief,
                request.user.is_superuser,
                request.user.is_task_operator
        )):
            users = users.exclude(id=request.user.id)
            lookups = [('all', _('All')), (None, request.user.username)]
        users = users.annotate(
            user=Exists(queryset.filter(to=OuterRef('pk')))
        ).filter(user=True).values_list('id', 'username').order_by('username')
        
        lookups.extend([(str(x[0]), x[1]) for x in users])
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"  
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if any((
                request.user.is_chief,
                request.user.is_superuser,
                request.user.is_task_operator
        )):
            if value is None:
                queryset = queryset.filter(to_id=request.user.id)
        if value and value != 'all':
            queryset = queryset.filter(to_id=value)

        return queryset


class TaskTagFilter(admfilters.TagFilter):

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        tag_ids = qs.values_list('tags__id', flat=True).distinct()
        objects = Tag.objects.filter(
            id__in=tag_ids).values_list('id', 'name').order_by('name')
        lookups = [*objects]
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"        
        return lookups

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(tags__id=self.value())
        return queryset


class IsActiveTaskFilter(admfilters.BoolFilter):
    title = _('Active')
    parameter_name = 'active'
    true_kwarg = {'stage__active': True}
    false_kwarg = {'stage__active': False}

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            (None, _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            qs = queryset.filter(**self.true_kwarg).distinct()
            if qs.model == Task:
                qs = hide_main_tasks(request, qs)
            return qs
        elif self.value() == 'no':
            return queryset.filter(**self.false_kwarg).distinct()
        return queryset
