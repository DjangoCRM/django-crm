import pandas as pd
from pathlib import Path
from typing import Union
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.utils.encoding import escape_uri_path
from django.utils.formats import date_format

from common.utils.helpers import get_today
from common.utils.helpers import get_verbose_name
from crm.models import Company
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead
from tasks.models import Task


def get_file_path(username: str, queryset: QuerySet = None, model=None) -> Path:
    today = get_today()
    file_path = settings.MEDIA_ROOT / 'exported'
    if queryset:
        file_name = f"{queryset.model.__name__}_db_{username}_{today}.xlsx"
    else:
        if not model:
            raise Exception("either queryset or model must be specified")
        file_name = f"{model.__name__}_db_{username}_{today}.xlsx"
    
    return file_path / escape_uri_path(file_name)


def get_columns_data() -> dict:
    return {
        ContentType.objects.get_for_model(Company).id: settings.COMPANY_COLUMNS,
        ContentType.objects.get_for_model(Contact).id: settings.CONTACT_COLUMNS,
        ContentType.objects.get_for_model(Deal).id: settings.DEAL_COLUMNS,
        ContentType.objects.get_for_model(Lead).id: settings.LEAD_COLUMNS,
        ContentType.objects.get_for_model(Task).id: settings.TASK_COLUMNS
    }


def export_objects_view(request: WSGIRequest) -> Union[HttpResponse, HttpResponseNotFound]:
    content_type_id = request.GET.get("content_type")
    content_type = ContentType.objects.get(id=content_type_id)
    queryset = content_type.model_class().objects.filter(
        owner=request.user
    )
    return export_selected_objects(request, queryset)


def export_selected_objects(request: WSGIRequest,
                            queryset: QuerySet) -> Union[HttpResponse, HttpResponseNotFound]:
    content_type = ContentType.objects.get_for_model(queryset.model)

    file_path = get_file_path(request.user.username, queryset)
    columns_data = get_columns_data()
    datadict = get_datadict(
        request,
        columns_data[content_type.id],
        queryset=queryset
    )
    save_to_excel(datadict, file_path)
    return get_export_response(file_path)


def save_to_excel(datadict: dict, file_path: Path) -> None:
    df = pd.DataFrame(datadict)
    df = df.replace('nan', '')
    df = df.replace('None', '')
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, 'Sheet1', index=False, na_rep=' ')
    writer.close()


def get_export_response(file_path: Path) -> Union[HttpResponse, HttpResponseNotFound]:
    if file_path.exists():
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + file_path.name
            return response

    return HttpResponseNotFound()


def get_datadict(request: WSGIRequest, columns,
                 obj=None, queryset: QuerySet = None) -> dict:
    datadict = dict()
    model = _get_model(obj, queryset)
    for attr in columns:
        objects = _get_object_iterator(request, obj, queryset)
    
        value_list = []
        for o in objects:
            if attr == 'industry':
                name_list = []
                for ind in o.industry.all():
                    name_list.append(ind.name)
                value = ",".join(name_list)
            else:
                value = getattr(o, attr)
            if attr in ('birth_date', 'was_in_touch', 'lead_time'):
                value = str(value)
            elif attr == 'creation_date':
                if model == Task:
                    value = date_format(
                        o.creation_date.date(),
                        format="SHORT_DATE_FORMAT",
                        use_l10n=True
                    )
                else:
                    value = str(o.creation_date.date()) if value else ''
            value_list.append(value)
        
        if model == Task:
            attr = get_verbose_name(model, attr)
        datadict[attr] = value_list
    return datadict


def _get_object_iterator(request: WSGIRequest, obj,
                         queryset: QuerySet) -> QuerySet:
    if obj:
        if request.user.is_superuser:
            objects = obj.objects.all().iterator()
        else:
            objects = obj.objects.filter(owner=request.user).iterator()
    elif queryset:
        objects = queryset.iterator()
    else:
        raise RuntimeError('Error: either object or queryset does not received')
    return objects


def _get_model(obj, queryset: QuerySet):
    if obj and obj.__class__ == Task:
        model = obj.__class__
    elif queryset:
        model = queryset.model
    return model    # NOQA
