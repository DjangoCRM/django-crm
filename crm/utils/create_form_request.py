from django.conf import settings
from django.db.models import Q

from common.models import Department
from common.utils.helpers import get_active_users
from common.utils.helpers import get_today
from common.utils.helpers import send_crm_email
from common.utils.parse_full_name import parse_full_name
from crm.forms.contact_form import ContactForm
from crm.models import Country
from crm.models import LeadSource
from crm.models import CrmEmail
from crm.models import Request
from crm.utils.check_city import check_city
from crm.utils.helpers import is_text_relevant
from crm.utils.ticketproc import new_ticket


def create_form_request(lead_source: LeadSource, form: ContactForm) -> None:
    data = form.cleaned_data
    ticket = new_ticket()
    department = lead_source.department
    if is_text_relevant(", ".join((data['subject'], data['message']))):
        request_email = _create_email(data, lead_source, department, ticket)
        request = _create_request(data, lead_source, department, ticket)
        country_name = data.get('country')
        if country_name and country_name != 'not _set':
            try:
                # re_str string must be acceptable for MySQL and PostgreSQL
                re_str = fr"(?:\s|^){country_name}(?:,|$)"
                request.country = Country.objects.get(
                    Q(name__iexact=country_name) |
                    Q(alternative_names__regex=re_str)
                )
            except Country.DoesNotExist:
                send_crm_email(
                    f"{settings.EMAIL_SUBJECT_PREFIX}Country name error.",
                    f"The DB does not contain Country object with name {country_name}.",
                    [adr[1] for adr in settings.ADMINS]
                )
            check_city(request, form)

        request.find_contact_or_lead()
        request.update_request_data()
        request.save()
        request_email.request = request
        request_email.owner = request.owner
        request_email.save()


def _create_email(data: dict, lead_source: LeadSource,
                  department: Department, ticket: str) -> CrmEmail:
    return CrmEmail(
        subject=data['subject'],
        incoming=True,
        from_field=data['email'],
        to=get_to_email(lead_source),
        content=f"""
From: {data['name']}

Phone: {data['phone']}

Email: {data['email']}

Company name: {data['company']}     

Message: {data['message']}                   
""",
        department=department,
        ticket=ticket,
        inquiry=True,
        is_html=False
    )


def _create_request(data: dict, lead_source: LeadSource,
                    department: Department, ticket: str) -> Request:

    first_name, middle_name, last_name = parse_full_name(data['name'])
    return Request(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=data['email'],
        request_for=data['subject'],
        phone=data['phone'],
        description=data['message'],
        company_name=data['company'],
        department=department,
        country=department.default_country,
        receipt_date=get_today(),
        lead_source=lead_source,
        ticket=ticket,
        city_name=data.get('city', '')
    )


def get_to_email(lead_source: LeadSource) -> str:
    to = ''
    if lead_source.email:
        to = lead_source.email
    else:
        operator = get_active_users().filter(
            groups__name='operators'
        ).first()
        if operator.email:
            to = operator.email
    return to
