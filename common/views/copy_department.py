from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse

from common.models import Department
from crm.models import ClientType
from crm.models import Industry
from crm.models import LeadSource
from crm.models import Product
from crm.models import ClosingReason
from crm.models import Stage
from crm.site.crmadminsite import crm_site


MODELS = [
    Product, Stage, ClosingReason,
    ClientType, Industry, LeadSource
]


def copy_department(request):
    """Creates a copy of the selected department."""
    if request.method == "POST":
        department_id = int(request.POST.get('department'))
        department = Department.objects.get(id=department_id)
        new_department_name = f"{department.name} (copy)"
        new_department = Department.objects.create(
            name=new_department_name,
            default_country=department.default_country,
            default_currency=department.default_currency,
            works_globally=department.works_globally
        )
        for model in MODELS:
            objects = model.objects.filter(
                department_id=department_id
            )
            for obj in objects:
                new_obj = obj
                new_obj.id = None
                new_obj.department = new_department
                new_obj.save()

        messages.info(
            request,
            _(
                "A new department has been created - {}. Please rename it."
            ).format(new_department_name)
        )
        return HttpResponseRedirect(
            reverse('admin:auth_group_changelist')
        )

    else:
        departments = Department.objects.all(
        ).order_by('name').values_list('id', 'name')

        extra_context = dict(
            crm_site.each_context(request),
            opts=Department._meta,
            departments=departments,
        )
    return render(request, 'common/copy_department.html', extra_context)
