from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.utils.helpers import get_today
from crm.models import Company, Contact, Deal, Lead, Stage, Tag as CrmTag
from crm.utils.ticketproc import new_ticket
from tasks.models import Project, ProjectStage, Task, TaskStage, Tag as TaskTag

from api.permissions import OwnedObjectPermission
from .serializers import (
    CompanySerializer,
    ContactSerializer,
    CrmTagSerializer,
    DealSerializer,
    LeadSerializer,
    ProjectSerializer,
    ProjectStageSerializer,
    StageSerializer,
    TaskSerializer,
    TaskStageSerializer,
    TaskTagSerializer,
    UserSerializer,
)

User = get_user_model()


def _has_field(model, field_name: str) -> bool:
    return any(field.name == field_name for field in model._meta.get_fields())


def _parse_bool(value):
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('1', 'true', 'yes', 'y'):
            return True
        if value_lower in ('0', 'false', 'no', 'n'):
            return False
    return value


def _filter_by_query_params(queryset, request, allowed_fields):
    params = request.query_params
    for field in allowed_fields:
        value = params.get(field)
        if value is None or value == '':
            continue
        queryset = queryset.filter(**{field: _parse_bool(value)})
    return queryset


def _get_default_department(user):
    return user.groups.first() if user and user.is_authenticated else None


class OwnedModelViewSet(viewsets.ModelViewSet):
    """Provides common owner/co-owner filtering and default owner assignment."""

    permission_classes = [IsAuthenticated, OwnedObjectPermission]
    owner_field = 'owner'
    co_owner_field = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs

        filters_q = Q()
        if self.owner_field:
            filters_q |= Q(**{self.owner_field: user})
        if self.co_owner_field:
            filters_q |= Q(**{self.co_owner_field: user})
        return qs.filter(filters_q)

    def _resolved_owner(self, provided_owner):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return provided_owner or user
        return user

    def _build_save_kwargs(self, serializer, extra_kwargs=None):
        kwargs = extra_kwargs.copy() if extra_kwargs else {}
        model = serializer.Meta.model
        owner_field = self.owner_field

        if owner_field:
            provided_owner = serializer.validated_data.get(owner_field)
            kwargs[owner_field] = self._resolved_owner(provided_owner)

        if _has_field(model, 'department') and 'department' not in kwargs:
            department = serializer.validated_data.get('department')
            if not department and owner_field and kwargs.get(owner_field):
                department = _get_default_department(kwargs[owner_field])
            if department:
                kwargs['department'] = department

        if _has_field(model, 'modified_by'):
            kwargs['modified_by'] = self.request.user

        return kwargs

    def perform_update(self, serializer):
        save_kwargs = {}
        if _has_field(serializer.Meta.model, 'modified_by'):
            save_kwargs['modified_by'] = self.request.user
        serializer.save(**save_kwargs)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['id', 'username', 'first_name', 'last_name']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TaskViewSet(OwnedModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.select_related(
        'project', 'stage', 'project__stage', 'owner', 'co_owner'
    ).prefetch_related('responsible', 'subscribers', 'tags').order_by('-update_date')
    co_owner_field = 'co_owner'
    filterset_fields = ['project', 'stage', 'active', 'owner', 'co_owner']
    search_fields = ['name', 'description', 'next_step', 'project__name']
    ordering_fields = ['next_step_date', 'due_date', 'creation_date', 'priority']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            qs = qs.filter(
                Q(owner=user) |
                Q(co_owner=user) |
                Q(responsible=user) |
                Q(subscribers=user)
            )
        qs = _filter_by_query_params(qs, self.request, ['project', 'stage', 'active', 'owner'])
        responsible_id = self.request.query_params.get('responsible')
        if responsible_id:
            qs = qs.filter(responsible__id=responsible_id)
        return qs.distinct()

    def perform_create(self, serializer):
        stage = serializer.validated_data.get('stage') or TaskStage.objects.filter(default=True).first()
        if not stage:
            raise ValidationError({'stage': 'Task stage is required. Provide a stage or create a default one.'})
        save_kwargs = self._build_save_kwargs(serializer, {'stage': stage})
        task = serializer.save(**save_kwargs)
        if not serializer.validated_data.get('responsible'):
            task.responsible.add(self.request.user)


class ProjectViewSet(OwnedModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.select_related(
        'stage', 'owner', 'co_owner'
    ).prefetch_related('responsible', 'subscribers', 'tags').order_by('-update_date')
    co_owner_field = 'co_owner'
    filterset_fields = ['stage', 'active', 'owner', 'co_owner']
    search_fields = ['name', 'description', 'next_step']
    ordering_fields = ['next_step_date', 'due_date', 'creation_date', 'priority']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            qs = qs.filter(
                Q(owner=user) |
                Q(co_owner=user) |
                Q(responsible=user) |
                Q(subscribers=user)
            )
        qs = _filter_by_query_params(qs, self.request, ['stage', 'active', 'owner'])
        responsible_id = self.request.query_params.get('responsible')
        if responsible_id:
            qs = qs.filter(responsible__id=responsible_id)
        return qs.distinct()

    def perform_create(self, serializer):
        stage = serializer.validated_data.get('stage') or ProjectStage.objects.filter(default=True).first()
        save_kwargs = self._build_save_kwargs(serializer, {'stage': stage} if stage else None)
        project = serializer.save(**save_kwargs)
        if not serializer.validated_data.get('responsible'):
            project.responsible.add(self.request.user)


class DealViewSet(OwnedModelViewSet):
    serializer_class = DealSerializer
    queryset = Deal.objects.select_related(
        'stage',
        'currency',
        'closing_reason',
        'lead',
        'contact',
        'company',
        'partner_contact',
        'country',
        'city',
        'owner',
        'co_owner',
        'department',
    ).prefetch_related('tags').order_by('-update_date')
    co_owner_field = 'co_owner'
    filterset_fields = ['company', 'stage', 'active', 'relevant', 'owner', 'co_owner', 'lead', 'contact']
    search_fields = [
        'name',
        'next_step',
        'description',
        'ticket',
        'company__full_name',
        'contact__first_name',
        'contact__last_name',
        'lead__first_name',
        'lead__last_name',
    ]
    ordering_fields = ['next_step_date', 'creation_date', 'amount', 'probability']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = _filter_by_query_params(
            qs,
            self.request,
            ['company', 'stage', 'active', 'relevant', 'owner', 'co_owner'],
        )
        contact_id = self.request.query_params.get('contact')
        if contact_id:
            qs = qs.filter(Q(contact_id=contact_id) | Q(partner_contact_id=contact_id))
        return qs

    def perform_create(self, serializer):
        stage = serializer.validated_data.get('stage') or Stage.objects.filter(default=True).first()
        next_step_date = serializer.validated_data.get('next_step_date') or get_today()
        ticket = serializer.validated_data.get('ticket') or new_ticket()

        save_kwargs = self._build_save_kwargs(
            serializer,
            {
                'stage': stage,
                'next_step_date': next_step_date,
                'ticket': ticket,
            },
        )
        serializer.save(**save_kwargs)


class LeadViewSet(OwnedModelViewSet):
    serializer_class = LeadSerializer
    queryset = Lead.objects.select_related(
        'lead_source', 'type', 'contact', 'company', 'owner', 'department', 'country', 'city'
    ).prefetch_related('industry', 'tags').order_by('-update_date')
    filterset_fields = ['owner', 'department', 'disqualified', 'company', 'lead_source', 'country']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    ordering_fields = ['creation_date', 'update_date', 'was_in_touch']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            departments = user.groups.all()
            qs = qs.filter(Q(owner=user) | Q(department__in=departments))

        qs = _filter_by_query_params(
            qs,
            self.request,
            ['owner', 'department', 'disqualified', 'company', 'lead_source'],
        )
        return qs.distinct()

    def perform_create(self, serializer):
        save_kwargs = self._build_save_kwargs(serializer)
        serializer.save(**save_kwargs)


class CompanyViewSet(OwnedModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.select_related(
        'owner', 'department', 'lead_source', 'country', 'city', 'type'
    ).prefetch_related('industry', 'tags').order_by('full_name')
    filterset_fields = ['owner', 'department', 'country', 'lead_source', 'disqualified', 'type']
    search_fields = ['full_name', 'alternative_names', 'website', 'email', 'phone']
    ordering_fields = ['full_name', 'creation_date', 'update_date']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            departments = user.groups.all()
            qs = qs.filter(Q(owner=user) | Q(department__in=departments))

        qs = _filter_by_query_params(
            qs,
            self.request,
            ['owner', 'department', 'country', 'lead_source', 'disqualified'],
        )
        return qs.distinct()

    def perform_create(self, serializer):
        save_kwargs = self._build_save_kwargs(serializer)
        serializer.save(**save_kwargs)


class ContactViewSet(OwnedModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.select_related(
        'company', 'owner', 'department', 'country', 'city'
    ).prefetch_related('tags').order_by('first_name', 'last_name')
    filterset_fields = ['owner', 'department', 'company', 'country', 'disqualified']
    search_fields = ['first_name', 'last_name', 'email', 'company__full_name', 'phone']
    ordering_fields = ['first_name', 'last_name', 'creation_date', 'update_date']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            departments = user.groups.all()
            qs = qs.filter(Q(owner=user) | Q(department__in=departments))

        qs = _filter_by_query_params(
            qs,
            self.request,
            ['owner', 'department', 'company', 'country', 'disqualified'],
        )
        return qs.distinct()

    def perform_create(self, serializer):
        save_kwargs = self._build_save_kwargs(serializer)
        serializer.save(**save_kwargs)


class TaskStageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskStageSerializer
    queryset = TaskStage.objects.all().order_by('index_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['index_number', 'name']


class ProjectStageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectStageSerializer
    queryset = ProjectStage.objects.all().order_by('index_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['index_number', 'name']


class StageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StageSerializer
    queryset = Stage.objects.all().order_by('index_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['index_number', 'name']
    filterset_fields = ['default', 'second_default', 'success_stage', 'conditional_success_stage', 'department']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        departments = user.groups.all()
        return qs.filter(department__in=departments)


class CrmTagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CrmTagSerializer
    queryset = CrmTag.objects.select_related('owner', 'department').all().order_by('name')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    filterset_fields = ['department', 'owner']

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        departments = user.groups.all()
        return qs.filter(Q(department__in=departments) | Q(owner=user))


class TaskTagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskTagSerializer
    queryset = TaskTag.objects.select_related('for_content').all().order_by('name')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'for_content__model']
    ordering_fields = ['name']
    filterset_fields = ['for_content']

    def get_queryset(self):
        qs = self.queryset
        model_filter = self.request.query_params.get('for_model')
        if model_filter:
            qs = qs.filter(for_content__model=model_filter)
        return qs
