from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _

from crm.site.crmadminsite import crm_site
from crm.models import Company, Contact
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL


def change_owner_companies(request):
    if request.method == "POST":
        owner_id = int(request.POST.get('owner'))
        owner = USER_MODEL.objects.get(id=owner_id)
        ids_str = request.GET.get('ids')
        ids = [int(x) for x in ids_str.split(',')]
        companies = Company.objects.filter(id__in=ids)
        department_id = get_department_id(owner)
        # "update_date" field needs to be updated
        # so don't use queryset.update()
        for company in companies.iterator():
            company.owner = owner
            company.department_id = department_id
            company.save()
        contacts = Contact.objects.filter(company_id__in=ids)
        for contact in contacts.iterator():
            contact.owner = owner
            contact.department_id = department_id
            contact.save()
        messages.info(
            request,
            _("Owner changed successfully")
        )
        return HttpResponseRedirect(request.GET.get('next'))
    else:
        owners = USER_MODEL.objects.filter(
            is_active=True,
            is_staff=True,
            groups__name='managers'
        ).order_by('username').values_list('id', 'username')
        extra_context = dict(
            crm_site.each_context(request),
            opts=Company._meta,
            owners=owners
        )
    return render(
        request, 'crm/change_owner_companies.html',
        extra_context
    )
