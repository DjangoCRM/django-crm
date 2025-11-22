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
from .validators import (
    ValidationMixin,
    validate_currency_amount,
    validate_date_range,
    validate_probability,
    validate_required_fields,
    validate_unique_email,
    validate_future_date,
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


class TaskSerializer(ValidationMixin, serializers.ModelSerializer):
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

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate required fields
        validate_required_fields(attrs, ['name'])
        
        # Validate date ranges
        if 'start_date' in attrs and 'due_date' in attrs:
            validate_date_range(attrs.get('start_date'), attrs.get('due_date'), 
                              ('start_date', 'due_date'))
        
        if 'due_date' in attrs and 'closing_date' in attrs:
            validate_date_range(attrs.get('due_date'), attrs.get('closing_date'),
                              ('due_date', 'closing_date'))
        
        return attrs

    def validate_next_step_date(self, value):
        """Validate next step date should be in future"""
        return validate_future_date(value, "Next step date")

    def validate_priority(self, value):
        """Validate task priority"""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError('Priority must be between 1 and 5')
        return value

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


class ProjectSerializer(ValidationMixin, serializers.ModelSerializer):
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

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate required fields
        validate_required_fields(attrs, ['name'])
        
        # Validate date ranges
        if 'start_date' in attrs and 'due_date' in attrs:
            validate_date_range(attrs.get('start_date'), attrs.get('due_date'),
                              ('start_date', 'due_date'))
        
        if 'due_date' in attrs and 'closing_date' in attrs:
            validate_date_range(attrs.get('due_date'), attrs.get('closing_date'),
                              ('due_date', 'closing_date'))
        
        return attrs

    def validate_next_step_date(self, value):
        """Validate next step date should be in future"""
        return validate_future_date(value, "Next step date")

    def validate_priority(self, value):
        """Validate project priority"""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError('Priority must be between 1 and 5')
        return value

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


class DealSerializer(ValidationMixin, serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate required fields
        validate_required_fields(attrs, ['name'])
        
        # Validate date ranges
        if 'closing_date' in attrs and 'win_closing_date' in attrs:
            validate_date_range(attrs.get('closing_date'), attrs.get('win_closing_date'), 
                              ('closing_date', 'win_closing_date'))
        
        return attrs

    def validate_amount(self, value):
        """Validate deal amount"""
        return validate_currency_amount(value)

    def validate_probability(self, value):
        """Validate deal probability"""
        return validate_probability(value)

    def validate_next_step_date(self, value):
        """Validate next step date should be in future"""
        return validate_future_date(value, "Next step date")

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


class LeadSerializer(ValidationMixin, serializers.ModelSerializer):
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
    full_name = serializers.CharField(read_only=True)

    def validate(self, attrs):
        """Cross-field validation"""
        # At least first_name or company_name is required
        if not attrs.get('first_name') and not attrs.get('company_name'):
            raise serializers.ValidationError(
                'Either first name or company name is required'
            )
        
        # Validate email uniqueness if provided
        if 'email' in attrs and attrs['email']:
            validate_unique_email(attrs['email'], Lead, self.instance)
        
        return attrs

    def validate_company_email(self, value):
        """Validate company email"""
        return self.validate_email(value) if value else value

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


class CompanySerializer(ValidationMixin, serializers.ModelSerializer):
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

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate required fields
        validate_required_fields(attrs, ['full_name'])
        
        # Validate email uniqueness if provided
        if 'email' in attrs and attrs['email']:
            validate_unique_email(attrs['email'], Company, self.instance)
        
        return attrs

    def validate_registration_number(self, value):
        """Validate company registration number"""
        if value:
            # Remove spaces and special characters
            cleaned = ''.join(c for c in value if c.isalnum())
            if len(cleaned) < 3:
                raise serializers.ValidationError('Registration number is too short')
        return value

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


class ContactSerializer(ValidationMixin, serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrmTag.objects.all(),
        required=False,
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=False,
    )
    full_name = serializers.CharField(read_only=True)

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate required fields
        validate_required_fields(attrs, ['first_name', 'last_name'])
        
        # Validate email uniqueness if provided
        if 'email' in attrs and attrs['email']:
            validate_unique_email(attrs['email'], Contact, self.instance)
        
        return attrs

    def validate_secondary_email(self, value):
        """Validate secondary email"""
        if value and value == self.initial_data.get('email'):
            raise serializers.ValidationError('Secondary email must be different from primary email')
        return self.validate_email(value) if value else value

    def validate_birth_date(self, value):
        """Validate birth date"""
        if value:
            from datetime import date
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 16:
                raise serializers.ValidationError('Contact must be at least 16 years old')
            if age > 120:
                raise serializers.ValidationError('Please check the birth date')
        
        return value

    def create(self, validated_data):
        # If no company is provided, use the default company
        if 'company' not in validated_data or validated_data['company'] is None:
            try:
                default_company = Company.objects.get(full_name='Default Company')
                validated_data['company'] = default_company
            except Company.DoesNotExist:
                # Fallback to first available company
                first_company = Company.objects.first()
                if first_company:
                    validated_data['company'] = first_company
                else:
                    raise serializers.ValidationError('No company available. Please create a company first.')
        
        return super().create(validated_data)

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
