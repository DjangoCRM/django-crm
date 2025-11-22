from django.contrib.auth import get_user_model
from rest_framework import serializers

from crm.models import (
    Company,
    Contact,
    Deal,
    Industry,
    Lead,
    Stage,
    Tag as CrmTag,
)
from tasks.models import (
    Project,
    ProjectStage,
    Task,
    TaskStage,
    Tag as TaskTag,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class TaskStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStage
        fields = ['id', 'name', 'default', 'done', 'in_progress', 'active', 'index_number']


class ProjectStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStage
        fields = ['id', 'name', 'default', 'done', 'in_progress', 'active', 'index_number']


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            'id',
            'name',
            'default',
            'index_number',
            'second_default',
            'success_stage',
            'conditional_success_stage',
            'goods_shipped',
            'department',
        ]


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ['id', 'name', 'for_content']
        read_only_fields = fields


class CrmTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrmTag
        fields = ['id', 'name', 'department', 'owner', 'creation_date', 'update_date']
        read_only_fields = ['creation_date', 'update_date']


class TaskSerializer(serializers.ModelSerializer):
    responsible = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    subscribers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TaskTag.objects.all(),
        required=False,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'name',
            'description',
            'note',
            'priority',
            'start_date',
            'due_date',
            'closing_date',
            'next_step',
            'next_step_date',
            'lead_time',
            'active',
            'remind_me',
            'project',
            'task',
            'stage',
            'owner',
            'co_owner',
            'responsible',
            'subscribers',
            'tags',
            'workflow',
            'creation_date',
            'update_date',
            'token',
        ]
        read_only_fields = ['workflow', 'creation_date', 'update_date', 'token']


class ProjectSerializer(serializers.ModelSerializer):
    responsible = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    subscribers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TaskTag.objects.all(),
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'note',
            'priority',
            'start_date',
            'due_date',
            'closing_date',
            'next_step',
            'next_step_date',
            'active',
            'remind_me',
            'stage',
            'owner',
            'co_owner',
            'responsible',
            'subscribers',
            'tags',
            'workflow',
            'creation_date',
            'update_date',
            'token',
        ]
        read_only_fields = ['workflow', 'creation_date', 'update_date', 'token']


class DealSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )

    class Meta:
        model = Deal
        fields = [
            'id',
            'name',
            'next_step',
            'next_step_date',
            'description',
            'workflow',
            'stage',
            'stages_dates',
            'closing_date',
            'win_closing_date',
            'amount',
            'currency',
            'closing_reason',
            'probability',
            'ticket',
            'city',
            'country',
            'lead',
            'contact',
            'request',
            'company',
            'partner_contact',
            'relevant',
            'active',
            'important',
            'tags',
            'is_new',
            'remind_me',
            'owner',
            'co_owner',
            'department',
            'creation_date',
            'update_date',
        ]
        read_only_fields = ['workflow', 'stages_dates', 'creation_date', 'update_date', 'ticket']


class LeadSerializer(serializers.ModelSerializer):
    industry = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Industry.objects.all(),
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'full_name',
            'title',
            'sex',
            'birth_date',
            'email',
            'secondary_email',
            'phone',
            'other_phone',
            'mobile',
            'city_name',
            'city',
            'country',
            'address',
            'region',
            'district',
            'description',
            'disqualified',
            'lead_source',
            'massmail',
            'tags',
            'token',
            'was_in_touch',
            'owner',
            'department',
            'company_name',
            'website',
            'company_phone',
            'company_address',
            'company_email',
            'type',
            'industry',
            'contact',
            'company',
            'creation_date',
            'update_date',
        ]
        read_only_fields = ['creation_date', 'update_date']


class CompanySerializer(serializers.ModelSerializer):
    industry = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Industry.objects.all(),
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )

    class Meta:
        model = Company
        fields = [
            'id',
            'full_name',
            'alternative_names',
            'website',
            'active',
            'phone',
            'city_name',
            'city',
            'registration_number',
            'country',
            'type',
            'industry',
            'address',
            'region',
            'district',
            'description',
            'disqualified',
            'email',
            'lead_source',
            'massmail',
            'tags',
            'token',
            'was_in_touch',
            'owner',
            'department',
            'creation_date',
            'update_date',
        ]
        read_only_fields = ['creation_date', 'update_date']


class ContactSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'full_name',
            'title',
            'sex',
            'birth_date',
            'email',
            'secondary_email',
            'phone',
            'other_phone',
            'mobile',
            'city_name',
            'city',
            'country',
            'address',
            'region',
            'district',
            'description',
            'disqualified',
            'lead_source',
            'massmail',
            'tags',
            'token',
            'was_in_touch',
            'owner',
            'department',
            'company',
            'creation_date',
            'update_date',
        ]
        read_only_fields = ['creation_date', 'update_date']
