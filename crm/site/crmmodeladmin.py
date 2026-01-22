import re
import threading
from typing import Union
from datetime import datetime as dt
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists
from django.db.models import Min
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from common.models import Department
from common.models import TheFile
from common.site.basemodeladmin import BaseModelAdmin
from common.utils.helpers import FRIDAY_SATURDAY_SUNDAY_MSG
from common.utils.helpers import get_active_users
from common.utils.helpers import get_department_id
from common.utils.helpers import get_manager_departments
from common.utils.helpers import LEADERS
from common.utils.helpers import popup_window
from crm.models import Company
from crm.models import ClientType
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead
from crm.models import LeadSource
from crm.models import Industry
from crm.models import Tag
from crm.models import Product
from crm.models import Stage
from crm.models import ClosingReason
from crm.models import CrmEmail
from crm.models.request import Request
from crm.utils.admfilters import ByVIPStatus
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from crm.utils.admfilters import TagFilter
from crm.utils.clarify_permission import clarify_permission
from crm.utils.helpers import html2txt
from crm.utils.admfilters import ByCityFilter
from crm.utils.admfilters import ByDepartmentFilter
from crm.utils.make_massmail_form import get_massmail_form
from massmail.admin_actions import BAD_RESULT_MSG
from massmail.admin_actions import have_massmail_accounts
from massmail.models import MailingOut

_thread_local = threading.local()
_fields = {
    'type': {'model': ClientType},
    'lead_source': {'model': LeadSource, 'order_by_field': '-name'},
    'stage': {'model': Stage},
    'closing_reason': {'model': ClosingReason}
}

website_tip = _("View website in new tab")
smartphone_callback = _("Callback to smartphone")
smartphone_callback_tip = _("Callback to your smartphone")

viber_chat = _("Viber chat")
viber_chat_tip = _("Chat or viber call")

whatsapp_chat = _("WhatsApp chat")
whatsapp_chat_tip = _("Chat or WhatsApp call")

email_icon = '<i title="{}" class="material-icons" style="color: var(--body-quiet-color)">email</i>'
email_title = _("Mailing list recipient.")
subscribed_icon = '<i title="{}" class="material-icons" style="font-size: small;color: var(--primary)">markunread_mailbox</i>'
subscribed_title = _("Signed up for email newsletters")
unsubscribed_icon = '<i title="{}" class="material-icons" style="font-size: small;color: var(--body-quiet-color)">markunread_mailbox</i>'
unsubscribed_title = _("Unsubscribed from email newsletters")
did_not_receive_icon = '<i title="{}" class="material-icons" style="font-size: small;color: var(--orange-fg)">markunread_mailbox</i>'
did_not_receive_title = _("The recipient has not received any mailings.")

class CrmModelAdmin(BaseModelAdmin):

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        if self.model in (Company, Contact, Lead):
            extra_context = extra_context or {}
            content_type_id = ContentType.objects.get_for_model(self.model).id
            extra_context['content_type_id'] = content_type_id

        elif self.model == Deal:
            # If the user selected a reason for closing deals in the filter,
            # check the deals activity filter to eliminate any discrepancies.
            query_dict = request.GET
            if "closing_reason__id__exact" in query_dict:
                active = query_dict.get('active')
                prev_query_dict = getattr(_thread_local, 'query_dict', {})
                qd = query_dict.copy()
                if active in (None, 'all'):
                    # Has the user selected an activity filter value?
                    prev_active = prev_query_dict.get('active')
                    if prev_active != active:
                        del qd['closing_reason__id__exact']
                    elif active is None:
                        qd['active'] = 'no'
                    return HttpResponseRedirect(
                        f"{reverse('site:crm_deal_changelist')}?{qd.urlencode()}"
                    )

        _thread_local.query_dict = request.GET
        _thread_local.query_path = request.path
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser or request.user.is_superoperator:
            if db_field.name in ('owner', 'co_owner'):
                kwargs["queryset"] = get_active_users().filter(
                    Q(is_superuser=True) |
                    Q(groups__name__in=('managers', 'operators', 'superoperators'))
                ).distinct()
            elif db_field.name in _fields:
                self.set_queryset(request, kwargs, **_fields[db_field.name])
        else:
            if db_field.name in ('owner', 'co_owner'):
                kwargs["queryset"] = get_active_users().filter(
                    groups=request.user.department_id,
                ).filter(
                    groups__name__in=(
                        'managers', 'operators', 'superoperators')
                ).distinct()
            elif db_field.name in _fields:
                kwargs["queryset"] = _fields[db_field.name]['model'].objects.filter(
                    department_id=request.user.department_id
                )
                if 'order_by_field' in _fields[db_field.name]:
                    kwargs["queryset"] = kwargs["queryset"].order_by(
                        _fields[db_field.name]['order_by_field']
                    )
        if db_field.name == 'department':
            kwargs["queryset"] = get_manager_departments()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            if db_field.name == "industry":
                self.set_queryset(request, kwargs, Industry)
        else:
            if db_field.name == "industry":
                kwargs["queryset"] = Industry.objects.filter(
                    department_id=request.user.department_id
                )
            elif db_field.name == "products":
                kwargs["queryset"] = Product.objects.filter(
                    department_id=request.user.department_id
                ).order_by('name')
        if db_field.name == "tags":
            kwargs["queryset"] = Tag.objects.filter(
                department_id=request.user.department_id
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.model in (Contact, Company, Lead, Deal):
            if 'owner' in request.GET and not request.user.is_superuser:
                return {}
        return actions

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['owner'] = request.user.id
        if hasattr(self.model, 'country') and 'country' not in initial and \
                request.user.department_id:
            initial['country'] = Department.objects.get(
                id=request.user.department_id
            ).default_country_id
        return initial

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and hasattr(obj, 'massmail'):
            if obj.massmail and 'massmail' in form.base_fields:
                label = form.base_fields['massmail'].label
                icon = subscribed_icon.format(subscribed_title)
                form.base_fields['massmail'].label = mark_safe(f"{label} {icon}")   
        return form

    def get_list_display(self, request):
        if self.model in (Request, Company, Contact, Lead):
            list_display = list(self.list_display)
            country_filter_needed = self.get_country_filter_needed(request)
            if country_filter_needed:
                list_display.insert(4, "the_country")
            else:
                list_display.insert(4, "the_city")
            return list_display

        return self.list_display

    def get_list_filter(self, request):
        list_filter = list(self.list_filter)
        if any((
                request.user.is_superuser,
                request.user.is_chief,
                request.user.is_superoperator,
                request.user.is_accountant
        )):
            if not list_filter.count(ByDepartmentFilter):
                list_filter.insert(0, ByDepartmentFilter)

        if self.model in (Deal, Request, Company, Contact, Lead):
            country_filter_needed = self.get_country_filter_needed(request)
            if country_filter_needed:
                list_filter.append(('country', ScrollRelatedOnlyFieldListFilter))
            if self.model in (Company, Contact, Lead):
                list_filter.extend(('massmail', ByVIPStatus))
            if hasattr(self.model, 'city'):
                if "country__id__exact" in request.GET or \
                        "city__id__exact" in request.GET or \
                        not country_filter_needed:
                    list_filter.append(ByCityFilter)
        if hasattr(self.model, 'tags'):
            if request.user.department_id or request.GET.get('department'):
                list_filter.append(TagFilter)
        
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.department_id:
            return qs.filter(department_id=request.user.department_id)
        elif request.user.is_superoperator:
            return qs.filter(
                department__in=request.user.groups.filter(
                    department__isnull=False
                )
            )
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and hasattr(obj, 'massmail'):
            if not obj.massmail:
                readonly_fields += ('unsubscribed',)

        return readonly_fields

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if value is False or not obj:
            return value
        return clarify_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        value = super().has_delete_permission(request, obj)
        if value is False or not obj:
            return value
        return clarify_permission(request, obj)

    # -- ModelAdmin callables -- #

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">phone_iphone</i>'
    ))
    def connections_to_mobile(self, obj):
        number = get_phone_number(obj, 'mobile')
        return self.connections(number) if number else LEADERS

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">contact_phone</i>'
    ))
    def connections_to_other_phone(self, instance):
        number = get_phone_number(instance, 'other_phone')
        return self.connections(number) if number else LEADERS

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">contact_phone</i>'
    ))
    def connections_to_phone(self, instance):
        number = get_phone_number(instance, 'phone')
        return self.connections(number) if number else LEADERS

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">contact_mail</i>'
    ))
    def create_email(self, obj):
        if obj.email and obj.id:
            model_name = self.model._meta.model_name  # NOQA
            url = reverse(
                'create_email',
                args=(obj.id,)
            ) + f"?object={model_name}&recipient={model_name}"
            title = _("Create Email")
            return mark_safe(
                f'<ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">\
                <li><a title="{title}" href="#" onClick="{popup_window(url)}">'
                f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">create</i> '
                f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">drafts</i>'
                f' </a></li></ul>'
            )
        return LEADERS

    @admin.display(description=mark_safe(
            '<i class="material-icons" style="color: var(--body-quiet-color)">business</i>'
        ),
        ordering='company_name'
    )
    def display_company_name(self, instance):
        return instance.company_name

    def make_massmail(self, request):
        """Cannot be used for Lead"""
        queryset = self.get_queryset(request)
        model = self.model
        if request.method == 'POST':
            form = get_massmail_form(request, model)
            form = form(request.POST)
            if form.is_valid():
                industries = form.cleaned_data['industries']
                countries = form.cleaned_data['countries']
                types = form.cleaned_data['types']
                before = dt.combine(form.cleaned_data['before'], dt.max.time())
                after = dt.combine(form.cleaned_data['after'], dt.min.time())
                current_tz = timezone.get_current_timezone()
                params = {
                    'country__in': countries,
                    'creation_date__gte': timezone.make_aware(after, current_tz),
                    'creation_date__lte': timezone.make_aware(before, current_tz),
                    'owner': request.user,
                    'massmail': True,
                    'disqualified': False
                }
                if model == Contact:
                    params['company__type__in'] = types
                    params['company__industry__in'] = industries

                else:  # Company
                    params['type__in'] = types
                    params['industry__in'] = industries

                qs = queryset.filter(**params)
                selected_ids = qs.values_list('id', flat=True).distinct()
                content_type = ContentType.objects.get_for_model(model)

                recipients_number = selected_ids.count()
                if recipients_number:
                    mailing_out = MailingOut(
                        name=settings.NO_NAME_STR,
                        recipient_ids=",".join([str(x) for x in selected_ids]),
                        recipients_number=recipients_number,
                        content_type=content_type,
                        owner=request.user,
                        department_id=request.user.department_id
                    )
                    mailing_out.save()
                    messages.info(request, _(FRIDAY_SATURDAY_SUNDAY_MSG)
                    )
                    return HttpResponseRedirect(reverse(
                        'site:massmail_mailingout_change',
                        args=(mailing_out.id,))
                    )
                messages.warning(request, _(BAD_RESULT_MSG))
        else:
            if not have_massmail_accounts(request):
                return HttpResponseRedirect(reverse(
                    'site:app_list',
                    args=('crm',))
                )
            min_date = None
            if queryset:
                min_date = queryset.aggregate(
                    min_date=Min('creation_date')
                )['min_date'].date()
            form = get_massmail_form(request, model, min_date)
            form = form()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
            app_label=model._meta.app_label,  # NOQA
            verbose_name=model._meta.verbose_name.title(),  # NOQA
            verbose_name_plural=model._meta.verbose_name_plural.title()  # NOQA
        )
        return TemplateResponse(request, 'crm/make_massmail.html', context)

    @admin.display(description=_('Messengers'))
    def messengers(self, obj):
        number = ''.join(re.findall(r"\+|\d+", obj.phone))
        if not number.count('+'):
            number = '+' + number

        return mark_safe(
            f'<ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">\
                <li><a title="{viber_chat_tip}" href="viber://chat/?number={number}">{viber_chat}</a></li>\
                <li><a title="{whatsapp_chat_tip}" href="https://wa.me/{number}/?text=Hi!" target="_blank">\
                {whatsapp_chat}</a></li>\
            </ul>'
        )

    @staticmethod
    @admin.display(description=mark_safe(
        email_icon.format(email_title)
    ))
    def newsletters_subscriptions(obj):
        if obj.massmail:
            if not obj.disqualified:
                content_type = ContentType.objects.get_for_model(obj.__class__)
                id_str = str(obj.id)
                is_mcs = MailingOut.objects.filter(
                    content_type=content_type,
                    successful_ids__regex=fr"(^|,){id_str}(,|$)"
                )
                if not is_mcs:
                    return mark_safe(
                        did_not_receive_icon.format(did_not_receive_title)
                    )
            return mark_safe(
                subscribed_icon.format(subscribed_title)
            )
        return mark_safe(
            unsubscribed_icon.format(unsubscribed_title)
        )

    @admin.display(description=mark_safe(
        f'<i class="material-icons" style="color: var(--body-quiet-color)">place</i>'),
        ordering='city'
    )
    def the_city(self, obj):
        if not obj.city:
            return LEADERS

        url_name = f"{obj.__class__.__name__}-{obj.city.name}"
        value = getattr(_thread_local, url_name, None)
        if not value:
            url = self.get_url_for_callable(
                'city__id__exact', obj.city.id)
            value = mark_safe(f'<a href="{url}">{obj.city.name}</a>')
            setattr(_thread_local, url_name, value)
        return value

    @admin.display(description=mark_safe(
        f'<i class="material-icons" style="color: var(--body-quiet-color)">place</i>'),
        ordering='country'
    )
    def the_country(self, obj):
        if not obj.country:
            return LEADERS

        url_name = f"{obj.__class__.__name__}-{obj.country.url_name}"
        value = getattr(_thread_local, url_name, None)
        if not value:
            url = self.get_url_for_callable(
                'country__id__exact', obj.country.id)
            value = mark_safe(f'<a href="{url}">{obj.country.name}</a>')
            setattr(_thread_local, url_name, value)
        return value

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">contact_mail</i>'
        ),
        ordering='email'
    )
    def the_email(self, instance):
        return instance.email

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">person_outline</i>'
        ),
        ordering='first_name'
    )
    def the_full_name(self, instance):
        if not instance.first_name:
            return LEADERS
        if getattr(instance, 'disqualified', None):
            return mark_safe(
                f'<span  style="color: var(--body-quiet-color)">{instance.full_name}</span>'
            )
        return instance.full_name

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">contact_phone</i>'
        ),
        ordering='phone'
    )
    def the_phone(self, instance):
        return instance.phone

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">public</i>'
    ))
    def view_website_button(self, instance):
        website_url = ''
        if hasattr(instance, 'website') and instance.website:
            website_url = instance.website.lower()
        if hasattr(instance, 'company') and instance.company.website:
            website_url = instance.company.website.lower()
        if website_url:
            if not website_url.startswith('http'):
                website_url = 'http://' + website_url
            li = f'<li><a title="{website_tip}" href="{website_url}" \
            target="_blank">{website_url}</a></li>'
            return mark_safe(
                f'<ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">{li}</ul>'
            )
        return LEADERS

    @staticmethod
    @admin.display(description=mark_safe(
        f"{_('Mass mailing')} "
        f"{unsubscribed_icon.format(unsubscribed_title)}"
    )) 
    def unsubscribed(instance):
        return unsubscribed_title

    # -- Custom methods -- #

    def connections(self, phone: str) -> str:
        number = ''.join(re.findall(r'\+|\d+', phone))
        if not number.count('+'):
            number = '+' + number
        onclick = f"window.open('/voip/get-callback/?number={number[1:]}', \
            '{phone}','width=800,height=700'); return false;"
        if self.model in (Contact, Lead, Company):
            phone = ''

        return mark_safe(
            f'''
            {phone}
                <ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">\
                    <li>
                        <a title="{smartphone_callback_tip}" href="#" onClick="{onclick}">\
                        {smartphone_callback}</a>
                    </li>\
                    <li><a title="{viber_chat_tip}" href="viber://chat/?number={number}">{viber_chat}</a></li>\
                    <li>
                        <a title="{whatsapp_chat_tip}" href="https://wa.me/{number}/?text=Hi!" target="_blank">
                            {whatsapp_chat}
                        </a>\
                    </li>
                </ul>
            '''
        )

    def del_dup_url(self, request: WSGIRequest, object_id: int) -> str:
        """Returns url of delete duplicate view"""
        content_type_id = ContentType.objects.get_for_model(self.model).id
        url = reverse("delete_duplicate", args=(content_type_id, object_id))
        query_string = request.META.get('QUERY_STRING', '')
        if query_string:
            url = f"{url}?{query_string}"
        return url

    def get_country_filter_needed(self, request: WSGIRequest) -> bool:
        attr = f"num_countries_dep_id{request.user.department_id}"  # NOQA
        country_filter_needed = getattr(_thread_local, attr, None)
        if country_filter_needed is None:
            qs = self.get_queryset(request)     # NOQA
            num_countries = qs.exclude(
                country__isnull=True
            ).values('country').distinct().count()
            if num_countries <= 1:
                country_filter_needed = False
            else:
                country_filter_needed = True
            setattr(_thread_local, attr, country_filter_needed)
        return country_filter_needed

    @staticmethod
    def get_latest_emails(field: str, object_id: int) -> QuerySet:
        kwargs = {field: object_id, 'trash': False}
        crmemail_type = ContentType.objects.get_for_model(CrmEmail)
        emails = CrmEmail.objects.filter(
            **kwargs
        ).order_by('-creation_date')[:4].annotate(
            is_attachment=Exists(
                TheFile.objects.filter(
                    content_type__pk=crmemail_type.id,
                    object_id=OuterRef('pk'))
            )
        )
        for e in emails:
            if e.is_html:
                e.content = html2txt(e.content)
        return emails

    @staticmethod
    def get_url_for_callable(parameter: str, value) -> str:
        query_dict = _thread_local.query_dict.copy()
        if query_dict.__contains__(parameter):
            query_dict.__setitem__(parameter, value)
        else:
            query_dict.update({parameter: value})
        query_string = query_dict.urlencode()
        return f"{_thread_local.query_path}?{query_string}"

    @staticmethod
    def massmail_field_name(obj) -> str:
        if obj and not obj.massmail:
            return 'unsubscribed'
        return 'massmail'

    
    def set_queryset(self, request: WSGIRequest, kwargs,
                     model, order_by_field: str = '') -> None:
        try:
            obj_id = request.resolver_match.kwargs['object_id']
            obj = self.model.objects.get(id=obj_id)
            department_id = None
            if obj.owner:
                department_id = get_department_id(obj.owner)
            elif obj.department:
                department_id = obj.department_id
            kwargs["queryset"] = model.objects.filter(
                department_id=department_id
            )
            if order_by_field:
                kwargs["queryset"] = kwargs["queryset"].order_by(
                    order_by_field)
        except KeyError:
            pass


def get_phone_number(obj: Union[Contact, Deal, Lead], attr: str) -> str:
    number = ''
    if obj.__class__ == Deal:
        if obj.contact:
            number = getattr(obj.contact, attr)
        else:
            number = getattr(obj.lead, attr)
    elif obj.__class__ in (Contact, Lead):
        number = getattr(obj, attr)

    return number
