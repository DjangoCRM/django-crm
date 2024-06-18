import re
from typing import Union
from django.core.mail import mail_admins
from django.db.models import Q

from crm.forms.admin_forms import CompanyForm
from crm.forms.admin_forms import LeadForm
from crm.forms.admin_forms import RequestForm
from crm.forms.contact_form import ContactForm
from crm.models import City
from crm.models import Company
from crm.models import Lead
from crm.models import Request


def check_city(obj: Union[Request, Company, Lead], 
               form: Union[ContactForm, RequestForm, LeadForm, CompanyForm]) -> None:

    if obj.country:
        if form.__class__ == ContactForm or 'city_name' in form.changed_data:
            if obj.city_name:
                obj.city_name = re.sub(r"[.,]$", '', obj.city_name.strip())

                # re_str string must be acceptable for MySQL and PostgreSQL
                re_str = fr"(?:\s|^){obj.city_name}(?:,|$)"
                cities = City.objects.filter(
                    Q(name__iexact=obj.city_name) |
                    Q(alternative_names__regex=re_str),
                    country=obj.country
                )
                obj.city = cities.first()
                
                if not obj.city:
                    city = City.objects.create(
                        country=obj.country,
                        name=obj.city_name
                    )
                    obj.city = city
                
                elif len(cities) > 1:
                    mail_admins(
                        "Error: check_city - MultipleObjectsReturned",
                        f'''
                        \nCity name: {obj.city_name}
                        \nException: City.MultipleObjectsReturned''',
                        fail_silently=False,
                    )
                
    elif obj.city and not obj.city_name:
        obj.city_name = obj.city.name
