from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.filters import DateFieldListFilter
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CharField
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Value as V  # NOQA
from django.db.models.functions import Cast
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import Department
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from common.utils.helpers import LEADERS
from crm.models import Contact
from crm.models import Product
from crm.models import Tag
from crm.models import Output
from crm.models.country import City
from massmail.models import MassContact

# Lookup parameters must be removed from the querystring when
# the corresponding filter is executed!


class ByCityFilter(SimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('City')
    parameter_name = 'city__id__exact'

    def lookups(self, request, model_admin):
        result = []
        qs = model_admin.get_queryset(request)
        country_id = request.GET.get("country__id__exact")
        if country_id:
            qs = qs.filter(country_id=country_id)
        is_null = qs.filter(city_id=None).exists()
        if is_null:
            qs = qs.exclude(city_id=None)

        cities = qs.values_list(
            'city_id', 'city__name'
        ).order_by('city__name').distinct()
        city_id = request.GET.get(self.parameter_name)

        if city_id and city_id != 'IsNull':
            try:
                city = cities.get(city_id=city_id)
                cities = cities.exclude(city_id=city_id)
            except ObjectDoesNotExist:
                city = City.objects.filter(
                    id=city_id
                ).values_list('id', 'name').first()
            result.append(city)

        elif city_id == 'IsNull':
            result.append(('IsNull', LEADERS))

        result.extend([*cities])
        if is_null:
            result.append(('IsNull', LEADERS))

        return result

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'IsNull':
            return queryset.filter(city_id__isnull=True)

        return queryset.filter(city_id=int(self.value()))


class ByVIPStatus(SimpleListFilter):
    """ Filter by recipients' VIP status. """
    title = _('VIP Status')
    parameter_name = 'vip_status'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('VIP')),
            ('no', _('Non-VIP')),
        )

    def queryset(self, request, queryset):
        if self.value():
            content_type = ContentType.objects.get_for_model(queryset.model)
            ids = queryset.values_list('id', flat=True)
            mcs = MassContact.objects.filter(
                object_id__in=ids,
                content_type=content_type,
            )
        if self.value() == 'yes':
            vip_ids = mcs.filter(
                email_account__main=True
            ).values_list('object_id', flat=True)
            return queryset.filter(id__in=list(vip_ids))
        if self.value() == 'no':
            non_vip_ids = mcs.filter(
                email_account__main=False
            ).values_list('object_id', flat=True)
            return queryset.filter(id__in=list(non_vip_ids))
        return queryset


class ChoicesSimpleListFilter(SimpleListFilter):
    """
    The SimpleListFilter with overridden "choices" method
    """

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def lookups(self, request, model_admin):
        """
        Must be overridden to return a list of tuples (value, verbose value)
        """
        raise NotImplementedError(
            "The SimpleListFilter.lookups() method must be overridden to "
            "return a list of tuples (value, verbose value)."
        )

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        raise NotImplementedError(
            "subclasses of ListFilter must provide a queryset() method"
        )


class ByCountryFilter(ChoicesSimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Country')
    parameter_name = 'country__id__exact'

    def lookups(self, request, model_admin):
        result = [('all', _('All'))]
        department_id = request.user.department_id
        default_country = None
        if department_id:
            default_country = Department.objects.get(
                id=department_id).default_country
        qs = model_admin.get_queryset(request)
        country_id = request.GET.get(self.parameter_name)
        is_null = qs.filter(country_id=None).exists()
        if is_null:
            qs = qs.exclude(country_id=None)

        countries = qs.distinct().annotate(
            str_id=Cast('country_id', output_field=CharField())
        ).values_list(
            'str_id', 'country__name'
        ).order_by('country__name')

        if country_id not in (None, 'all', 'IsNull'):
            country = countries.get(country_id=country_id)
            countries = countries.exclude(country_id=country_id)
            result.append(country)

        elif country_id is None:
            if default_country:
                result.append((None, default_country.name))
            else:
                result = [(None, _('All'))]

        result.extend([*countries])
        if is_null or country_id == 'IsNull':
            result.append(('IsNull', LEADERS))

        return result

    def queryset(self, request, queryset):
        value = self.value()
        department_id = request.user.department_id
        default_country_id = None
        if not value:
            if department_id:
                default_country_id = Department.objects.get(
                    id=department_id).default_country_id
            if default_country_id:
                return queryset.filter(country_id=default_country_id)
            return queryset

        if value == 'all':
            return queryset

        if value == 'IsNull':
            return queryset.filter(country_id__isnull=True)

        return queryset.filter(country_id=int(self.value()))


class CrmDateFieldListFilter(DateFieldListFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "admin/crm_date_filter.html"
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        #  zone, so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.date()

        self.links = list(self.links)
        self.links.insert(
            4,
            (_('Last month'), {
                self.lookup_kwarg_since: str(
                    (today + relativedelta(months=-1)).replace(day=1)
                ),
                self.lookup_kwarg_until: str(today.replace(day=1))
            })
        )
        self.links.insert(
            5,
            (_('First half of the year'), {
                self.lookup_kwarg_since: str(
                    today.replace(month=1, day=1)
                ),
                self.lookup_kwarg_until: str(today.replace(month=7, day=1))
            })
        )
        self.links.insert(
            6,
            (_('Nine months of this year'), {
                self.lookup_kwarg_since: str(
                    today.replace(month=1, day=1)
                ),
                self.lookup_kwarg_until: str(today.replace(month=10, day=1))
            })
        )
        sh = (
            (_('Second half of the last year'), {
                self.lookup_kwarg_since: str(today.replace(
                    year=today.year - 1, month=7, day=1)
                ),
                self.lookup_kwarg_until: str(today.replace(month=1, day=1)),
            })
        )
        if len(self.links) > 8:
            self.links.insert(8, sh)
        else:
            self.links += (sh,)


class ScrollRelatedOnlyFieldListFilter(admin.RelatedOnlyFieldListFilter):
    template = "crm/filter_scroll.html"


class TagFilter(SimpleListFilter):
    title = _('Tag')
    parameter_name = 'tags__id'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        department_id = request.user.department_id
        if department_id:
            qs = qs.filter(department_id=department_id)
        username = request.GET.get('owner')
        if username and username != 'all':
            if username == 'IsNull':
                qs = qs.filter(owner__isnull=True)
            else:
                qs = qs.filter(owner__username=username)
        if not any((request.user.is_superuser, request.user.is_chief, username)):
            qs = qs.filter(owner=request.user)
        tag_ids = qs.values_list('tags__id', flat=True).distinct()
        objects = Tag.objects.filter(
            id__in=tag_ids
        ).values_list('id', 'name').order_by('name')
        lookups = [*objects]
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            queryset = queryset.filter(tags__id=value)
        return queryset


class ByProductFilter(SimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Product')
    parameter_name = 'product__id__exact'

    def lookups(self, request, model_admin):
        products = Product.objects.all()
        department_id = request.GET.get(
            'department') or request.user.department_id
        if department_id and department_id != 'all':
            products = products.filter(
                department_id=int(department_id)
            )
        products = products.values_list('id', 'name').order_by('name')
        return [*products]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        deal_ids = Output.objects.filter(
            product_id=int(self.value())
        ).values_list('deal_id', flat=True)
        return queryset.filter(id__in=list(deal_ids))


class ByDepartmentFilter(SimpleListFilter):
    title = _('Department')
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        if self.value() is None:
            department_id = request.user.department_id
            value = str(department_id) if department_id else None
            self.used_parameters[self.parameter_name] = value
        if request.user.is_superoperator:
            departments = request.user.groups.all()
        else:
            departments = request.user.groups.model.objects.all()
        departments = departments.filter(
            department__isnull=False,
            user__groups__name='managers'
        ).distinct().annotate(
            str_id=Cast('id', output_field=CharField())
        ).values_list('str_id', 'name').order_by('name')
        return [('all', _('All')), *departments]

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup or not self.value() and lookup == 'all',
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    def queryset(self, request, queryset):
        value = self.value()

        if value in ('all', None):
            return queryset

        if hasattr(queryset.model, 'department_id'):
            return queryset.filter(department_id=value)

        if hasattr(queryset.model, 'deal'):
            return queryset.filter(deal__department_id=value)

        return queryset


class PaymentByDepartmentFilter(ByDepartmentFilter):

    def queryset(self, request, queryset):
        value = self.value()
        if value in ('all', None):
            return queryset
        return queryset.filter(deal__department_id=value)


class ByOwnerFilter(ChoicesSimpleListFilter):
    title = _('Owner')
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        lookups = [(None, _('All'))]
        deal_id = request.GET.get('deal__id__exact')
        if deal_id:
            qs = qs.filter(deal_id=int(deal_id))
        request_id = request.GET.get('request__id__exact')
        if request_id:
            qs = qs.filter(request_id=int(request_id))
        if not any((
                request.user.is_superuser,
                request.user.is_superoperator,
                request.user.is_chief and not request.user.is_manager,
                request.user.is_task_operator,
                request.user.is_accountant
        )) and not any((deal_id, request_id)):
            q_params = Q(owner=request.user)
            if hasattr(qs.model, 'co_owner'):
                q_params |= Q(co_owner=request.user)
            qs = qs.exclude(q_params)
            lookups = [('all', _('All')), (None, request.user.username)]

        lookups.extend(self.get_owner_lookups(qs))
        if qs.filter(owner=None).exists():
            lookups.append(('IsNull', LEADERS))
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"
        return lookups

    @staticmethod
    def get_owner_lookups(queryset: QuerySet) -> list:
        q_params = Q(owner=OuterRef('pk'))
        if hasattr(queryset.model, 'co_owner'):
            q_params |= Q(co_owner=OuterRef('pk'))
        filtered_qs = queryset.filter(q_params)
        owners = USER_MODEL.objects.annotate(
            user=Exists(filtered_qs)
        ).filter(user=True).values_list(
            'username', flat=True).order_by('username')

        return [(x, x) for x in owners]

    def queryset(self, request, queryset):
        if not any((
                request.user.is_superuser,
                request.user.is_superoperator,
                request.user.is_chief and not request.user.is_manager,
                request.user.is_task_operator,
                request.user.is_accountant
        )):
            if self.value() is None and not any((
                    request.GET.get('deal__id__exact'),
                    request.GET.get('request__id__exact')
            )):
                return self.get_owner_queryset(queryset, request.user.username)

        if self.value() in (x[1] for x in self.lookup_choices):
            return self.get_owner_queryset(queryset, self.value())

        if self.value() == 'IsNull':
            return queryset.filter(owner=None)
        return queryset

    @staticmethod
    def get_owner_queryset(queryset, username):
        q_params = Q(owner__username=username)
        if hasattr(queryset.model, 'co_owner'):
            q_params |= Q(co_owner__username=username)
        return queryset.filter(q_params)


class ByChangedByChiefs(ChoicesSimpleListFilter):
    title = _('changed by chiefs')
    parameter_name = 'changed_by_chief'

    def lookups(self, request, model_admin):
        return (
            (None, _('All')),
            ('yes', _('Yes')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            chiefs = USER_MODEL.objects.filter(
                groups__name='chiefs'
            ).values_list('id', flat=True)
            return queryset.filter(modified_by__in=chiefs)
        return queryset


class ByPartnerFilter(SimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Partner')
    parameter_name = 'partner_contact__id'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        un = request.GET.get('owner')
        if un:
            qs = qs.filter(owner__username=un)
        if not any((request.user.is_superuser, request.user.is_chief, un)):
            qs = qs.filter(owner=request.user)
        partner_ids = qs.values_list('partner_contact_id', flat=True)
        objects = Contact.objects.filter(id__in=partner_ids).annotate(
            screen_name=Concat(
                'first_name', V(' '), 'last_name', V(', '),
                'company__full_name', V(', '), 'country__name',
                output_field=CharField()
            )).values_list('id', 'screen_name').order_by('first_name')
        return [*objects, ('IsNull',  _('No'))]

    def queryset(self, request, queryset):
        if self.value() == 'IsNull':
            return queryset.filter(partner_contact_id__isnull=True)

        if self.value() is not None:
            return queryset.filter(partner_contact_id=self.value())

        return queryset


class BoolFilter(ChoicesSimpleListFilter):
    true_kwarg = {'myfield': True}
    false_kwarg = {'myfield': False}

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            (None, _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(**self.true_kwarg).distinct()
        if self.value() == 'no':
            return queryset.filter(**self.false_kwarg).distinct()
        return queryset


class ImportantFilter(BoolFilter):
    title = _('Important')
    parameter_name = 'important'
    true_kwarg = {'important': True}

    def lookups(self, request, model_admin):
        return (
            (None, _('All')),
            ('yes', _('Yes')),
        )


class HasContactsFilter(BoolFilter):
    title = _('Has Contacts')
    parameter_name = 'has_contacts'
    true_kwarg = {'contacts__isnull': False}
    false_kwarg = {'contacts__isnull': True}

    def lookups(self, request, model_admin):
        return (
            (None, _('All')),
            ('yes', _('Yes')),
            ('no', _('No')),
        )


class IsDisqualifiedFilter(BoolFilter):
    title = _('Disqualified')
    parameter_name = 'disqualified'
    true_kwarg = {'disqualified': True}
    false_kwarg = {'disqualified': False}

    def lookups(self, request, model_admin):
        return (
            (None, _('All')),
            ('yes', _('Yes')),
            ('no', _('No')),
        )


class IsActiveFilter(BoolFilter):
    title = _('Active')
    parameter_name = 'active'
    true_kwarg = {'active': True}
    false_kwarg = {'active': False}

    def lookups(self, request, model_admin):
        if any((
                request.GET.get("company__id__exact"),
                request.GET.get("contact__id__exact"),
                request.GET.get("lead__id__exact"),
        )):
            return (
                (None, _('All')),
                ('yes', _('Yes')),
                ('no', _('No')),
            )
        return (
            ('all', _('All')),
            (None, _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if any((
                request.GET.get("company__id__exact"),
                request.GET.get("contact__id__exact"),
                request.GET.get("lead__id__exact"),
        )):
            if self.value() is None:
                return queryset
        if self.value() is None:
            return queryset.filter(**self.true_kwarg).distinct()
        elif self.value() == 'no':
            return queryset.filter(**self.false_kwarg).distinct()
        return queryset


class MailboxFilter(SimpleListFilter):
    title = _('mailbox')
    parameter_name = 'mailbox'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        q_params = Q(sent=False, incoming=False, trash=False)
        department_id = request.user.department_id
        if department_id:
            q_params &= Q(department_id=department_id)
        username = request.GET.get('owner')
        if username and username not in ('all', 'IsNull'):
            owner = USER_MODEL.objects.get(username=username)
            if not department_id or department_id == get_department_id(owner):
                q_params &= Q(owner__username=username)
        else:
            if not any((request.user.is_superuser, request.user.is_chief)):
                q_params &= Q(owner=request.user)
        num = qs.filter(q_params).count()
        return (
            ('inbox', _('inbox')),
            ('sent', _('sent')),
            ('outbox', _(f'outbox ({num})')),
            ('trash', _('trash')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'inbox':
            return queryset.filter(incoming=True, trash=False)
        if self.value() == 'sent':
            return queryset.filter(sent=True, trash=False)
        if self.value() == 'outbox':
            return queryset.filter(sent=False, incoming=False, trash=False)
        if self.value() == 'trash':
            return queryset.filter(trash=True)
