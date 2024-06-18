import re
from email.utils import parseaddr
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import connection
from django.db.utils import IntegrityError
from crm.models import Company
from crm.models import ClientType
from crm.models import Country
from crm.models import Industry
from crm.models import LeadSource
from crm.utils.helpers import DateForm
from crm.utils.helpers import get_owner
from common.utils.helpers import save_message


class HashMyAttr:

    def __init__(self, obj):
        self.obj = obj
        self.industry_list = []

    def __hash__(self):
        data = self.get_data(self)
        return data.__hash__()

    def __eq__(self, other):
        return self.get_data(self) == self.get_data(other)

    @staticmethod
    def get_data(value):
        data = value.obj.full_name
        if value.obj.email:
            data = data + value.obj.email
        if value.obj.country:
            country_name = value.obj.country.name
            return data + country_name
        else:
            return data


def create_objects(request, df1, **kwargs):
    obj = kwargs['object']
    objs = [HashMyAttr(obj()) for _ in range(len(df1.index))]

    try:
        for column in kwargs['columns']:
            if column in df1.columns:
                for obj, value in zip(objs, df1[column]):
                    value = str(value).strip(' ')
                    value = re.sub(r"[\r\n]", '', value)
                    if column == 'industry':
                        industry_list = []
                        if value:
                            for name in [v for v in value.split(',')]:
                                name = name.strip()
                                try:
                                    ind = Industry.objects.get(name=name)
                                    industry_list.append(ind)
                                except ObjectDoesNotExist:
                                    pass
                        obj.industry_list = industry_list
                    else:
                        if column == 'country':
                            value = Country.objects.filter(name=value).first()
                        elif column == 'company':
                            try:
                                if obj.obj.owner:
                                    value = Company.objects.get(
                                        full_name=value, owner=obj.obj.owner)
                                elif obj.obj.country:
                                    value = Company.objects.get(
                                        full_name=value, country=obj.obj.country)
                            except Exception as e:  # ObjectDoesNotExist, MultipleObjectsReturned
                                save_message(
                                    request.user, f"Error with: {value} - {e}.", 'ERROR')
                                value = None
                        elif column == 'owner':
                            value = get_owner(request, value)
                        elif column == 'type':
                            value = ClientType.objects.filter(name=value).first()
                        elif column == 'department':
                            value = Group.objects.filter(name=value).first()
                        elif column == 'birth_date' or column == 'was_in_touch':
                            try:
                                form = DateForm({'birth_date': value})
                                if form.is_valid():
                                    value = form.cleaned_data['birth_date']
                                else:
                                    value = None
                            except ValidationError:
                                value = None
                        elif column == 'lead_source':
                            value = LeadSource.objects.filter(name=value).first()
                        setattr(obj.obj, column, value)
        # objs = list(set(objs))
        for obj in objs:
            msg = lev = ''
            # if 'uniq1' in kwargs and 'uniq1' in kwargs:
            kw = {
                f'{kwargs["uniq1"]}': getattr(obj.obj, kwargs['uniq1']),
                f'{kwargs["uniq2"]}': getattr(obj.obj, kwargs['uniq2']),
            }
            o = kwargs['object'].objects.filter(**kw)
            if o:
                msg, lev = f'Already exists: {obj.obj.full_name} ({obj.obj.country})', 'INFO'
            elif kwargs["attr"] == 'contact':
                try:
                    _ = obj.obj.company
                except obj.obj.DoesNotExist:
                    msg = f"Error with: {obj.obj.full_name} ({obj.obj.country}). Company was not assigned"
                    lev = 'ERROR'
            elif parseaddr(obj.obj.email)[1] == '':
                msg = f"Invalid email address: {obj.obj.full_name} ({obj.obj.country})."
                lev = 'ERROR'
            if msg:
                save_message(request.user, msg, lev)
                continue
            if obj.obj.owner:
                setattr(obj.obj, 'created_by', obj.obj.owner)
                setattr(obj.obj, 'modified_by', obj.obj.owner)
            else:
                setattr(obj.obj, 'created_by', request.user)
                setattr(obj.obj, 'modified_by', request.user)
            try:
                obj.obj.save()
                if hasattr(obj.obj, 'industry'):
                    obj.obj.industry.set(obj.industry_list, clear=True)
            except IntegrityError:
                msg = f'IntegrityError: {obj.obj.full_name}'
                save_message(request.user, msg, 'ERROR')
    except Exception as e:
        mail_admins(
            "Exception in create_objects",
            f"""
            \nException: {e}
            """,
            fail_silently=True,
        )
    connection.close()
