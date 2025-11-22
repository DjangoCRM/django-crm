from __future__ import annotations

from typing import Optional, Tuple
from django.contrib.auth import get_user_model
from django.db import transaction

from crm.models import Lead, Contact, Company, LeadSource
from common.models import Department


def _get_or_create_lead_source(name: str) -> Optional[LeadSource]:
    ls = LeadSource.objects.filter(name=name).first()
    if ls:
        return ls
    dept = Department.objects.first()
    if not dept:
        return None
    return LeadSource.objects.create(name=name, department=dept)


@transaction.atomic
def ensure_lead_and_contact(
    *,
    source_name: str,
    display_name: str,
    phone: str = '',
    email: str = '',
    company_name: Optional[str] = None,
) -> Tuple[Lead, Contact]:
    """
    Create minimal Lead and Contact (with Company) if not exist by phone.
    If phone is empty, we still create Lead based on display_name.
    """
    lead_source = _get_or_create_lead_source(source_name)

    # Lead: try to find by phone in phone/mobile
    lead = None
    if phone:
        lead = Lead.objects.filter(phone__icontains=phone).first() or \
               Lead.objects.filter(mobile__icontains=phone).first()
    if not lead:
        first_name = display_name or (phone or 'Unknown')
        lead = Lead.objects.create(
            first_name=first_name[:100],
            phone=phone or '',
            mobile=phone or '',
            email=email or '',
            lead_source=lead_source,
            description=f'Auto-created from {source_name}',
        )

    # Contact requires Company; make lightweight company and contact
    contact = None
    if phone:
        contact = Contact.objects.filter(phone__icontains=phone).first() or \
                  Contact.objects.filter(mobile__icontains=phone).first()
    if not contact:
        comp_name = company_name or f'{source_name} Client'
        company = Company.objects.filter(full_name=comp_name).first()
        if not company:
            company = Company.objects.create(
                full_name=comp_name[:200],
                email=email or '',
                phone=phone or '',
            )
        contact = Contact.objects.create(
            company=company,
            first_name=(display_name or (phone or 'Unknown'))[:100],
            phone=phone or '',
            mobile=phone or '',
            email=email or '',
        )
    return lead, contact
