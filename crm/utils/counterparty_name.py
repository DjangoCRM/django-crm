from email.utils import parseaddr
from django.db.models import CharField
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat

from crm.models import Contact
from crm.models import Company
from crm.models import CrmEmail
from crm.models import Lead


def get_counterparty_name(email: CrmEmail) -> str:
    """
    If the email address (the first one if the address list)
    does not contain a recipient name, then performs a search
    and returns the name of the first match among
    Contact, Lead, and Company.
    """
    if email.sent:
        addresses = email.to or email.cc
    else:
        addresses = email.from_field
    address_list = addresses.split(",")
    name, email_addr = parseaddr(address_list.pop(0))
    if not name:
        email_params = Q(email__icontains=email_addr)
        email_params |= Q(secondary_email__icontains=email_addr)
        func = Concat(
            "first_name", 
            Value(" "),
            "last_name",
            output_field=CharField()
        )
        contact = Contact.objects.filter(email_params).annotate(
            full_name=func
        )
        lead = Lead.objects.filter(email_params).annotate(
            full_name=func
        )
        company = Company.objects.filter(email__icontains=email)
        name = CrmEmail.objects.filter(id=email.id).annotate(
            contact_name=Subquery(contact.values(
                "full_name")[:1],
                output_field=CharField()
            ),
            lead_name=Subquery(
                lead.values("full_name")[:1],
                output_field=CharField()
            ),
            company_name=Subquery(
                company.values("full_name")[:1],
                output_field=CharField()
            )
        ).annotate(
            full_name=Coalesce(
                "contact_name",
                "lead_name",
                "company_name"
            )
        ).first().full_name
        if name:
            address_list.insert(0, f"{name} <{email_addr}>")
            addresses = ",".join(address_list)
    return addresses
