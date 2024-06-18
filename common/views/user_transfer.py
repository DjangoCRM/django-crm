from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from crm.models import Company
from crm.models import Contact
from crm.models import ClientType
from crm.models import Deal
from crm.models import Industry
from crm.models import Lead
from crm.models import CrmEmail
from crm.models import Product
from crm.models import ClosingReason
from crm.models import Request
from crm.models import Stage
from crm.models import Tag
from crm.site.crmadminsite import crm_site
from massmail.models import EmailAccount
from massmail.models import EmlMessage
from massmail.models import MailingOut
from massmail.models import Signature


WARNING_MESSAGE = _("""
Attention! Data for filters such as: 
transaction stages, reasons for closing, tags, etc. 
will be transferred only if the new department has data with the same name.
Also Output, Payment and Product will not be affected.
""")


objects = (
    {
        'model': Request,
        # 'fk': (('lead_source', LeadSource),),
        'm2m': (('products', Product),)
    },
    {
        'model': Deal,
        'fk': (('stage', Stage), ('closing_reason', ClosingReason)),
        'm2m': (('tags', Tag),)
    },
    {
        'model': Company,
        'fk': (('type', ClientType),),
        'm2m': (('industry', Industry), ('tags', Tag))
    },
    {
        'model': Contact,
        'm2m': (('tags', Tag),)
    },
    {
        'model': Lead,
        'fk': (('type', ClientType),),
        'm2m': (('industry', Industry), ('tags', Tag))
    },
    {'model': CrmEmail},
    {'model': EmailAccount},
    {'model': MailingOut},
    {'model': Signature},
    {'model': EmlMessage}
)


def user_transfer(request):
    """Change user's and its documents department. 
    But no change Output, Payment and Product."""
    if request.method == "POST":
        owner_id = int(request.POST.get('owner'))
        owner = USER_MODEL.objects.get(id=owner_id)
        old_department = owner.groups.filter(
            department__isnull=False
        ).first()
        new_department = Group.objects.get(
            id=int(request.POST.get('department'))
        )
        owner.groups.remove(old_department)
        owner.groups.add(new_department)
        for item in objects:
            changed_num = item['model'].objects.filter(owner=owner).update(
                department=new_department
            )
            if changed_num != 0:
                instances = item['model'].objects.filter(owner=owner)
                for instance in instances:
                    if 'fk' in item:
                        is_instance_changed = False
                        for attr, related_model in item['fk']:
                            old_attr_value = getattr(instance, attr)
                            if old_attr_value:
                                try:
                                    new_attr_value = related_model.objects.get(
                                        department=new_department,
                                        name=old_attr_value.name
                                    )
                                    setattr(instance, attr, new_attr_value)
                                    is_instance_changed = True
                                except ClientType.DoesNotExist:
                                    pass
                        if is_instance_changed:
                            instance.save()
                    for attr, related_model in item.get('m2m', []):
                        old_attrs = getattr(instance, attr).all()
                        old_attr_values = list(
                            old_attrs.values_list('name', flat=True)
                        )
                        if old_attr_values:
                            if related_model == Tag:
                                for tag in old_attrs:
                                    tag.department = new_department
                                    tag.save()
                            else:
                                new_attr_values = related_model.objects.filter(
                                    department=new_department,
                                    name__in=old_attr_values
                                )
                                if new_attr_values:
                                    getattr(instance, attr).set(
                                        new_attr_values,
                                        clear=True
                                    )
                                else:
                                    getattr(instance, attr).clear()

        messages.info(
            request,
            _("User transferred successfully")
        )
        return HttpResponseRedirect(
            reverse('admin:auth_user_changelist')
        )

    else:
        owners = USER_MODEL.objects.filter(
            is_active=True,
            is_staff=True,
            groups__name__in=('managers', 'operators')
        ).distinct().order_by('username').values_list('id', 'username')
        departments = Group.objects.filter(
            department__isnull=False
        ).order_by('name').values_list('id', 'name')

        extra_context = dict(
            crm_site.each_context(request),
            opts=USER_MODEL._meta,    # NOQA
            owners=owners,
            departments=departments,
            warning_message=WARNING_MESSAGE
        )
    return render(request, 'common/user_transfer.html', extra_context)
