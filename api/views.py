from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import HttpResponse
import csv
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.utils.helpers import get_today
from crm.models import Company, Contact, Deal, Lead, Stage, Tag as CrmTag
from crm.utils.ticketproc import new_ticket
from tasks.models import Memo, Project, ProjectStage, Task, TaskStage, Tag as TaskTag
from chat.models import ChatMessage
from crm.models.others import CallLog
from .serializers import CallLogSerializer

from api.permissions import OwnedObjectPermission
from .serializers import (
    ChatMessageSerializer,
    CompanySerializer,
    ContactSerializer,
    CrmTagSerializer,
    DealSerializer,
    LeadSerializer,
    MemoSerializer,
    ProjectSerializer,
    ProjectStageSerializer,
    StageSerializer,
    TaskSerializer,
    TaskStageSerializer,
    TaskTagSerializer,
    UserSerializer,
)

User = get_user_model()


@extend_schema(tags=['Call Logs'])
@extend_schema(
    tags=['Call Logs'],
    description='Create and list telephony call logs.'
)
class CallLogViewSet(viewsets.ModelViewSet):
    """API endpoint to view and create call logs."""
    serializer_class = CallLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number']
    ordering_fields = ['timestamp', 'duration']

    def get_queryset(self):
        qs = self.request.user.call_logs.all().order_by('-timestamp')
        params = self.request.query_params
        # Filter by direction
        direction = params.get('direction')
        if direction in ('inbound', 'outbound'):
            qs = qs.filter(direction=direction)
        # Filter by number (contains)
        number = params.get('number')
        if number:
            qs = qs.filter(number__icontains=number)
        # Date range
        date_from = _norm_date(params.get('date_from'))
        date_to = _norm_date(params.get('date_to'))
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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


def _norm_date(value):
    """Normalize incoming date string to YYYY-MM-DD or return None if invalid."""
    if not value:
        return None
    v = str(value).strip()
    # already YYYY-MM-DD
    try:
        datetime.strptime(v, '%Y-%m-%d')
        return v
    except ValueError:
        pass
    # ISO with time
    try:
        return datetime.fromisoformat(v.replace('Z', '+00:00')).date().isoformat()
    except ValueError:
        pass
    return None


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


@extend_schema(tags=['Shared'])
@extend_schema(
    tags=['Shared'],
    description='Common owner/co-owner behavior for CRUD viewsets.'
)
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


@extend_schema(tags=['Users'])
@extend_schema(
    tags=['Users'],
    description='Read-only user directory.'
)
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


@extend_schema(tags=['Tasks'])
@extend_schema(
    tags=['Tasks'],
    description='CRUD for tasks with filtering and ordering.'
)
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


@extend_schema(tags=['Projects'])
@extend_schema(
    tags=['Projects'],
    description='CRUD for projects and related filtering.'
)
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
        # extra date filters
        params = self.request.query_params
        date_from = _norm_date(params.get('date_from'))
        date_to = _norm_date(params.get('date_to'))
        if date_from:
            qs = qs.filter(creation_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(creation_date__date__lte=date_to)
        due_from = _norm_date(params.get('due_from'))
        due_to = _norm_date(params.get('due_to'))
        if due_from:
            qs = qs.filter(due_date__gte=due_from)
        if due_to:
            qs = qs.filter(due_date__lte=due_to)
        return qs.distinct()

    def perform_create(self, serializer):
        stage = serializer.validated_data.get('stage') or ProjectStage.objects.filter(default=True).first()
        save_kwargs = self._build_save_kwargs(serializer, {'stage': stage} if stage else None)
        project = serializer.save(**save_kwargs)
        if not serializer.validated_data.get('responsible'):
            project.responsible.add(self.request.user)

    def list(self, request, *args, **kwargs):
        view_mode = request.query_params.get('view')
        if view_mode == 'compact':
            qs = self.filter_queryset(self.get_queryset()).only('id', 'name', 'active', 'due_date', 'next_step', 'next_step_date', 'creation_date')
            data = [
                {
                    'id': o.id,
                    'name': o.name,
                    'status': 'active' if o.active else 'done',
                    'due_date': o.due_date,
                    'next_step': o.next_step,
                    'next_step_date': o.next_step_date,
                    'created': o.creation_date,
                }
                for o in qs[: int(request.query_params.get('limit', 50))]
            ]
            return Response({'count': len(data), 'results': data})
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        project = self.get_object()
        done_stage = ProjectStage.objects.filter(done=True).first()
        if done_stage:
            project.stage = done_stage
        project.active = False
        project.closing_date = get_today()
        project.next_step = 'Done'
        project.next_step_date = get_today()
        project.save()
        return Response({'status': 'completed', 'id': project.id})

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        project = self.get_object()
        default_stage = ProjectStage.objects.filter(default=True).first() or ProjectStage.objects.filter(in_progress=True).first()
        if default_stage:
            project.stage = default_stage
        project.active = True
        project.closing_date = None
        project.save()
        return Response({'status': 'reopened', 'id': project.id})

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('owner')
        if not user_id:
            raise ValidationError({'owner': 'owner is required'})
        try:
            new_owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError({'owner': 'User not found'})
        project.owner = new_owner
        project.save(update_fields=['owner', 'update_date'])
        return Response({'status': 'assigned', 'id': project.id, 'owner': new_owner.id})

    @action(detail=False, methods=['post'])
    def bulk_tag(self, request):
        ids = request.data.get('ids') or []
        tags = request.data.get('tags') or []
        if not ids or not tags:
            raise ValidationError({'detail': 'ids and tags are required'})
        qs = self.get_queryset().filter(id__in=ids)
        tag_objs = TaskTag.objects.filter(id__in=tags)
        updated = 0
        for obj in qs:
            obj.tags.add(*tag_objs)
            updated += 1
        return Response({'status': 'ok', 'updated': updated})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.filter_queryset(self.get_queryset())
        fields = ['id','name','active','due_date','next_step','next_step_date','creation_date']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'
        writer = csv.writer(response)
        writer.writerow(fields)
        for o in qs.iterator():
            writer.writerow([
                o.id,
                o.name,
                o.active,
                o.due_date,
                o.next_step,
                o.next_step_date,
                o.creation_date,
            ])
        return response


@extend_schema(tags=['Deals'])
@extend_schema(
    tags=['Deals'],
    description='CRUD for CRM deals with ownership rules.'
)
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
    filterset_fields = ['company', 'stage', 'active', 'relevant', 'owner', 'co_owner', 'lead', 'contact', 'department']
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


@extend_schema(tags=['Leads'])
@extend_schema(
    tags=['Leads'],
    description='CRUD for CRM leads with filtering and conversion actions.'
)
class LeadViewSet(OwnedModelViewSet):
    serializer_class = LeadSerializer
    queryset = Lead.objects.select_related(
        'lead_source', 'type', 'contact', 'company', 'owner', 'department', 'country', 'city'
    ).prefetch_related('industry', 'tags').order_by('-update_date')
    filterset_fields = ['owner', 'department', 'disqualified', 'company', 'lead_source', 'country', 'was_in_touch']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone', 'company_phone']
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
            ['owner', 'department', 'disqualified', 'company', 'lead_source', 'was_in_touch'],
        )
        # date_from/date_to filters by creation_date
        params = self.request.query_params
        date_from = _norm_date(params.get('date_from'))
        date_to = _norm_date(params.get('date_to'))
        if date_from:
            qs = qs.filter(creation_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(creation_date__date__lte=date_to)
        return qs.distinct()

    def perform_create(self, serializer):
        save_kwargs = self._build_save_kwargs(serializer)
        serializer.save(**save_kwargs)

    def list(self, request, *args, **kwargs):
        view_mode = request.query_params.get('view')
        if view_mode == 'compact':
            qs = self.filter_queryset(self.get_queryset()).only('id', 'first_name', 'last_name', 'company_name', 'disqualified', 'was_in_touch', 'creation_date')
            data = [
                {
                    'id': o.id,
                    'name': (o.first_name or '') + (' ' + o.last_name if o.last_name else '') if (o.first_name or o.last_name) else (o.company_name or ''),
                    'company': o.company_name,
                    'status': 'disqualified' if o.disqualified else 'active',
                    'was_in_touch': o.was_in_touch,
                    'created': o.creation_date,
                }
                for o in qs[: int(request.query_params.get('limit', 50))]
            ]
            return Response({'count': len(data), 'results': data})
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def disqualify(self, request, pk=None):
        lead = self.get_object()
        reason = request.data.get('reason', '')
        lead.disqualified = True
        if reason:
            lead.description = (lead.description or '') + f"\n[Disqualified] {reason}"
        lead.save(update_fields=['disqualified', 'description', 'update_date'])
        return Response({'status': 'disqualified', 'id': lead.id})

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        lead = self.get_object()
        user_id = request.data.get('owner')
        if not user_id:
            raise ValidationError({'owner': 'owner is required'})
        try:
            new_owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError({'owner': 'User not found'})
        lead.owner = new_owner
        lead.save(update_fields=['owner', 'update_date'])
        return Response({'status': 'assigned', 'id': lead.id, 'owner': new_owner.id})

    @action(detail=False, methods=['post'])
    def bulk_tag(self, request):
        ids = request.data.get('ids') or []
        tags = request.data.get('tags') or []
        if not ids or not tags:
            raise ValidationError({'detail': 'ids and tags are required'})
        qs = self.get_queryset().filter(id__in=ids)
        tag_objs = CrmTag.objects.filter(id__in=tags)
        for lead in qs:
            lead.tags.add(*tag_objs)
        return Response({'status': 'ok', 'updated': qs.count()})

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        lead = self.get_object()
        create_deal = _parse_bool(request.data.get('create_deal'))
        owner_id = request.data.get('owner')
        try:
            selected_owner = User.objects.get(pk=owner_id) if owner_id else request.user
        except User.DoesNotExist:
            selected_owner = request.user
        # Ensure company
        company = lead.company
        if not company and (lead.company_name or lead.company_email or lead.company_phone):
            company = Company.objects.create(
                full_name=lead.company_name or (lead.first_name or '') + ' ' + (lead.last_name or '') or 'Company',
                phone=lead.company_phone or '',
                address=lead.company_address or '',
                email=lead.company_email or '',
                owner=selected_owner,
                department=_get_default_department(selected_owner),
            )
        # Ensure contact
        contact = lead.contact
        if not contact and (lead.first_name or lead.last_name or lead.email or lead.phone or lead.mobile):
            contact = Contact.objects.create(
                first_name=lead.first_name or '',
                middle_name=lead.middle_name or '',
                last_name=lead.last_name or '',
                email=lead.email or '',
                phone=lead.phone or '',
                mobile=lead.mobile or '',
                company=company,
                owner=selected_owner,
                department=_get_default_department(selected_owner),
            )
        deal = None
        if create_deal:
            deal = Deal.objects.create(
                name=f"Deal with {contact.full_name if contact else (company.full_name if company else lead.full_name)}",
                company=company,
                contact=contact,
                lead=lead,
                owner=selected_owner,
                stage=Stage.objects.filter(default=True).first(),
                next_step_date=get_today(),
            )
        # Link back and mark was_in_touch
        if contact and not lead.contact:
            lead.contact = contact
        if company and not lead.company:
            lead.company = company
        lead.was_in_touch = True
        lead.save()
        return Response({
            'status': 'converted',
            'lead': lead.id,
            'contact': contact.id if contact else None,
            'company': company.id if company else None,
            'deal': deal.id if deal else None,
        })


@extend_schema(tags=['Companies'])
@extend_schema(
    tags=['Companies'],
    description='CRUD for companies with search and filters.'
)
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


@extend_schema(tags=['Contacts'])
@extend_schema(
    tags=['Contacts'],
    description='CRUD for contacts with search and filters.'
)
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


@extend_schema(tags=['Task Stages'])
@extend_schema(
    tags=['Task Stages'],
    description='Reference list of task stages.'
)
class TaskStageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskStageSerializer
    queryset = TaskStage.objects.all().order_by('index_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['index_number', 'name']


@extend_schema(tags=['Project Stages'])
@extend_schema(
    tags=['Project Stages'],
    description='Reference list of project stages.'
)
class ProjectStageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectStageSerializer
    queryset = ProjectStage.objects.all().order_by('index_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['index_number', 'name']


@extend_schema(tags=['Stages'])
@extend_schema(
    tags=['Stages'],
    description='Reference list of CRM deal stages.'
)
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


@extend_schema(tags=['CRM Tags'])
@extend_schema(
    tags=['CRM Tags'],
    description='Reference list of CRM tags.'
)
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


@extend_schema(tags=['Task Tags'])
@extend_schema(
    tags=['Task Tags'],
    description='Reference list of task tags.'
)
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


@extend_schema(tags=['Memos'])
@extend_schema(
    tags=['Memos'],
    description='CRUD for memos; includes archive and postpone actions.'
)
class MemoViewSet(OwnedModelViewSet):
    """
    ViewSet for managing memos (office memos/notes).
    Supports filtering by stage, recipient, and draft status.
    """
    serializer_class = MemoSerializer
    queryset = Memo.objects.select_related(
        'owner', 'to', 'task', 'project', 'deal', 'resolution'
    ).prefetch_related('tags', 'subscribers').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'note']
    ordering_fields = ['creation_date', 'update_date', 'review_date', 'name']
    ordering = ['-creation_date']
    filterset_fields = ['stage', 'draft', 'to', 'task', 'project', 'deal']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # Filter out drafts that don't belong to the current user
        qs = qs.filter(Q(draft=False) | Q(owner=user))
        
        # Additional filters from query params
        stage = self.request.query_params.get('stage')
        if stage:
            qs = qs.filter(stage=stage)
        
        # Filter by recipient
        to_user = self.request.query_params.get('to_user')
        if to_user:
            qs = qs.filter(to__id=to_user)
        
        # Filter by review date range
        review_date_from = self.request.query_params.get('review_date_from')
        review_date_to = self.request.query_params.get('review_date_to')
        if review_date_from:
            qs = qs.filter(review_date__gte=_norm_date(review_date_from))
        if review_date_to:
            qs = qs.filter(review_date__lte=_norm_date(review_date_to))
        
        return qs

    def perform_create(self, serializer):
        """Set the owner to the current user on create."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Mark a memo as reviewed."""
        memo = self.get_object()
        memo.stage = Memo.REVIEWED
        memo.save()
        return Response({'status': 'memo marked as reviewed'})

    @action(detail=True, methods=['post'])
    def mark_postponed(self, request, pk=None):
        """Mark a memo as postponed."""
        memo = self.get_object()
        memo.stage = Memo.POSTPONED
        memo.save()
        return Response({'status': 'memo marked as postponed'})


@extend_schema(tags=['Chat Messages'])
@extend_schema(
    tags=['Chat Messages'],
    description='Create, list, and manage internal chat messages.'
)
class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages.
    Supports filtering by content_object and threading (replies/topics).
    """
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.select_related(
        'owner', 'content_type', 'answer_to', 'topic'
    ).prefetch_related('recipients', 'to').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['creation_date']
    ordering = ['creation_date']
    filterset_fields = ['content_type', 'object_id', 'owner']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # Filter messages where user is owner, recipient, or mentioned in 'to'
        qs = qs.filter(
            Q(owner=user) | Q(recipients=user) | Q(to=user)
        ).distinct()
        
        # Additional filters from query params
        content_type_id = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        if content_type_id and object_id:
            qs = qs.filter(content_type_id=content_type_id, object_id=object_id)
        
        # Filter by topic (thread)
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            qs = qs.filter(Q(topic_id=topic_id) | Q(id=topic_id))
        
        # Filter root messages only (no replies)
        root_only = self.request.query_params.get('root_only')
        if root_only and _parse_bool(root_only):
            qs = qs.filter(answer_to__isnull=True)
        
        return qs

    def perform_create(self, serializer):
        """Set the owner to the current user on create."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get all replies to a specific message."""
        message = self.get_object()
        replies = ChatMessage.objects.filter(answer_to=message).order_by('creation_date')
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """Get all messages in a thread (topic)."""
        message = self.get_object()
        topic = message.topic if message.topic else message
        thread_messages = ChatMessage.objects.filter(
            Q(topic=topic) | Q(id=topic.id)
        ).order_by('creation_date')
        serializer = self.get_serializer(thread_messages, many=True)
        return Response(serializer.data)


# Common helpers for Dashboard filters (period/owner/department)

def _parse_period(params):
    """Return date_from based on period param (7d,30d,90d) else None."""
    period = params.get('period', '').lower()
    now = timezone.now()
    if period == '7d':
        return now - timedelta(days=7)
    if period == '30d':
        return now - timedelta(days=30)
    if period == '90d':
        return now - timedelta(days=90)
    return None


def _apply_owner_department_filters(qs, request):
    owner = request.query_params.get('owner')
    department = request.query_params.get('department')
    if owner:
        qs = qs.filter(owner_id=owner)
    if department:
        qs = qs.filter(department_id=department)
    return qs


# Dashboard Analytics Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['Dashboard'],
    description='Returns KPI metrics for dashboard. Filters: period(7d|30d|90d), owner, department.',
    parameters=[
        OpenApiParameter(name='period', description='Time window', required=False, type=str, examples=[
            OpenApiExample('7d', value='7d'),
            OpenApiExample('30d', value='30d'),
            OpenApiExample('90d', value='90d'),
        ]),
        OpenApiParameter(name='owner', description='Filter by owner id', required=False, type=int),
        OpenApiParameter(name='department', description='Filter by department id', required=False, type=int),
    ],
)
def dashboard_analytics(request):
    """
    Provides analytics data for the dashboard including monthly growth stats
    and task metrics.
    Supports filters: period(7d|30d|90d), owner, department.
    """
    user = request.user
    date_from = _parse_period(request.query_params)

    # Base QuerySets with RBAC scope
    if user.is_superuser or user.is_staff:
        contacts_qs = Contact.objects.all()
        companies_qs = Company.objects.all()
        deals_qs = Deal.objects.all()
        tasks_qs = Task.objects.all()
    else:
        departments = user.groups.all()
        contacts_qs = Contact.objects.filter(Q(owner=user) | Q(department__in=departments))
        companies_qs = Company.objects.filter(Q(owner=user) | Q(department__in=departments))
        deals_qs = Deal.objects.filter(Q(owner=user) | Q(co_owner=user))
        tasks_qs = Task.objects.filter(
            Q(owner=user) | Q(co_owner=user) | Q(responsible=user) | Q(subscribers=user)
        )

    # Apply owner/department filters from query
    contacts_qs = _apply_owner_department_filters(contacts_qs, request)
    companies_qs = _apply_owner_department_filters(companies_qs, request)
    deals_qs = _apply_owner_department_filters(deals_qs, request)
    tasks_qs = _apply_owner_department_filters(tasks_qs, request)

    # Apply period filter
    if date_from:
        contacts_qs = contacts_qs.filter(creation_date__gte=date_from)
        companies_qs = companies_qs.filter(creation_date__gte=date_from)
        deals_qs = deals_qs.filter(creation_date__gte=date_from)
        tasks_qs = tasks_qs.filter(creation_date__gte=date_from)

    contacts_growth = contacts_qs.count()
    companies_growth = companies_qs.count()
    deals_growth = deals_qs.count()

    # Task metrics
    today = timezone.now().date()
    active_tasks = tasks_qs.filter(active=True).count()
    overdue_tasks = tasks_qs.filter(active=True, due_date__lt=today).count()

    # Compose simple series for revenue/deals/leads if needed (placeholder)
    # The frontend tolerates absence; we return minimal structure.
    return Response({
        'monthly_growth': {
            'contacts': contacts_growth,
            'companies': companies_growth,
            'deals': deals_growth,
        },
        'tasks': {
            'active': active_tasks,
            'overdue': overdue_tasks,
        }
    })


# Dashboard Activity Feed Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['Dashboard'],
    description='Returns recent activity feed. Supports filters: owner, department, limit.',
    parameters=[
        OpenApiParameter(name='owner', description='Filter by owner id', required=False, type=int),
        OpenApiParameter(name='department', description='Filter by department id', required=False, type=int),
        OpenApiParameter(name='limit', description='Max items to return', required=False, type=int, examples=[
            OpenApiExample('20', value=20),
        ]),
    ],
)
def dashboard_activity(request):
    """
    Provides a real-time activity feed showing recent changes across the CRM.
    Returns a list of activities sorted by timestamp.
    """
    user = request.user
    limit = int(request.query_params.get('limit', 10))
    
    activities = []
    
    # Filter based on user permissions
    if user.is_superuser or user.is_staff:
        deals_qs = Deal.objects.all()
        tasks_qs = Task.objects.all()
        contacts_qs = Contact.objects.all()
        companies_qs = Company.objects.all()
    else:
        departments = user.groups.all()
        deals_qs = Deal.objects.filter(Q(owner=user) | Q(co_owner=user))
        tasks_qs = Task.objects.filter(
            Q(owner=user) | Q(co_owner=user) | Q(responsible=user) | Q(subscribers=user)
        )
        contacts_qs = Contact.objects.filter(Q(owner=user) | Q(department__in=departments))
        companies_qs = Company.objects.filter(Q(owner=user) | Q(department__in=departments))
    
    # Get user's recent deals (last 3) - only created/updated by current user
    recent_deals = deals_qs.filter(owner=user).select_related('owner').order_by('-update_date')[:3]
    for deal in recent_deals:
        activities.append({
            'type': 'deal_updated',
            'message': f'You updated deal "{deal.name}"',
            'timestamp': deal.update_date.isoformat() if deal.update_date else deal.creation_date.isoformat(),
            'icon': 'fas fa-handshake',
            'color': 'success'
        })
    
    # Get user's recent tasks (last 3) - only owned by current user
    recent_tasks = tasks_qs.filter(owner=user).select_related('owner', 'stage').order_by('-update_date')[:3]
    for task in recent_tasks:
        is_completed = not task.active
        activities.append({
            'type': 'task_completed' if is_completed else 'task_updated',
            'message': f'You {("completed" if is_completed else "updated")} task "{task.name}"',
            'timestamp': task.update_date.isoformat() if task.update_date else task.creation_date.isoformat(),
            'icon': 'fas fa-check' if is_completed else 'fas fa-tasks',
            'color': 'success' if is_completed else 'warning'
        })
    
    # Get user's recent contacts (last 2) - only created by current user
    recent_contacts = contacts_qs.filter(owner=user).select_related('owner').order_by('-creation_date')[:2]
    for contact in recent_contacts:
        full_name = f"{contact.first_name} {contact.last_name}".strip() or "Unnamed Contact"
        activities.append({
            'type': 'contact_created',
            'message': f'You added contact "{full_name}"',
            'timestamp': contact.creation_date.isoformat(),
            'icon': 'fas fa-user-plus',
            'color': 'primary'
        })
    
    # Get user's recent companies (last 2) - only created by current user
    recent_companies = companies_qs.filter(owner=user).select_related('owner').order_by('-creation_date')[:2]
    for company in recent_companies:
        activities.append({
            'type': 'company_created',
            'message': f'You added company "{company.full_name}"',
            'timestamp': company.creation_date.isoformat(),
            'icon': 'fas fa-building',
            'color': 'info'
        })
    
    # Sort all activities by timestamp (most recent first) and limit
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activities[:limit])


# Dashboard Funnel Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['Dashboard'],
    description='Returns sales funnel data grouped by stage. Filters: period(7d|30d|90d), owner, department.',
    parameters=[
        OpenApiParameter(name='period', description='Time window', required=False, type=str, examples=[
            OpenApiExample('7d', value='7d'),
            OpenApiExample('30d', value='30d'),
            OpenApiExample('90d', value='90d'),
        ]),
        OpenApiParameter(name='owner', description='Filter by owner id', required=False, type=int),
        OpenApiParameter(name='department', description='Filter by department id', required=False, type=int),
    ],
    examples=[
        OpenApiExample(
            'FunnelExample',
            summary='Funnel by stage',
            value=[
                {'label': 'New', 'value': 12},
                {'label': 'Qualified', 'value': 7},
                {'label': 'Won', 'value': 3},
            ],
        )
    ],
)
def dashboard_funnel(request):
    """
    Returns sales funnel data as a list of {label, value} by deal stage.
    Supports filters: period(7d|30d|90d), owner, department.
    RBAC: non-staff users see only owned/co-owned deals.
    """
    user = request.user
    date_from = _parse_period(request.query_params)

    # Base queryset with RBAC scope
    if user.is_superuser or user.is_staff:
        qs = Deal.objects.all()
    else:
        qs = Deal.objects.filter(Q(owner=user) | Q(co_owner=user))

    qs = _apply_owner_department_filters(qs, request)
    if date_from:
        qs = qs.filter(creation_date__gte=date_from)

    # Group by stage and count
    stages = Stage.objects.all().order_by('index_number')
    data = []
    stage_counts = qs.values('stage').annotate(cnt=Count('id'))
    count_map = {row['stage']: row['cnt'] for row in stage_counts}
    for st in stages:
        data.append({'label': st.name, 'value': count_map.get(st.id, 0)})

    return Response(data)
