from email.message import EmailMessage
from email.utils import format_datetime
from random import random
from typing import Tuple

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import models
from django.utils import timezone
from common.utils.helpers import USER_MODEL
from crm.models import Country


def get_email_message() -> Tuple[EmailMessage, str, str]:
    msg = EmailMessage()
    msg.add_header('Date', format_datetime(timezone.now()))
    content = str(random())
    msg.set_content(content)
    subject_str = f'The content - {content}'
    msg['Subject'] = subject_str
    msg['From'] = 'me@example.com'
    msg['To'] = 'you@example.com'
    msg['Message-ID'] = f"<{content}@example.com>"
    return msg, content, subject_str


def get_country_instance():
    country = Country.objects.first()
    if not country:
        country = Country.objects.create(
            name='United States',
            url_name='United-States'
        )
    return country


def get_user():
    user = USER_MODEL.objects.create(
        username="Andrew.Manager.Global",
        email="andrew@example.com",
        is_staff=True,
        is_active=True,
    )
    user.groups.set([1, 7, 9])
    return user


def get_txt_inmemoryfile(name: str) -> Tuple[str, SimpleUploadedFile]:
    file_name = f'{name}_{int(random() * 1E5)}.txt'
    file = SimpleUploadedFile(
        file_name, b"file_content", content_type="text/plain")
    return file_name, file


def add_file_to_form(name: str, form_data: dict) -> str:
    file_name, file = get_txt_inmemoryfile(name)
    form_data['common-thefile-content_type-object_id-TOTAL_FORMS'] = '1'
    form_data['common-thefile-content_type-object_id-0-file'] = file
    return file_name


def attach_file_to_email_msg(msg: EmailMessage) -> str:
    file_name = get_random_file_name()
    msg.add_attachment("Text of content", filename=file_name)
    return file_name


def get_content_file(name: str) -> Tuple[str, ContentFile]:
    file_name = f'{name}_{int(random() * 1E5)}.txt'
    return file_name, ContentFile("hello world", name=file_name)


def fk_field(initial):
    if type(initial) in (str, int):
        return str(initial)
    return str(initial.id)


def m2m_field(initial):
    if type(initial[0]) is int:
        return [str(x) for x in initial]
    else:
        return [str(x.id) for x in initial]


field_func = {
    models.ModelChoiceField: fk_field,
    models.ModelMultipleChoiceField: m2m_field,
}


def get_random_file_name() -> str:
    return f'test_file{int(random() * 1E5)}.txt'


def get_form_initials(form, data: dict):
    for key, value in form.base_fields.items():
        if value.initial is not None:
            if value.__class__ in field_func:
                func = field_func[value.__class__]
                data[key] = func(value.initial)
            else:
                _set_form_initial_value(form, data, key, value.initial)

    if 'token' in data:
        data['token'] = data['token']()
    if getattr(form, 'declared_fields'):
        for key, value in form.declared_fields.items():
            if value.initial is not None:
                data[key] = value.initial
    initials = form.initial
    for key, value in initials.items():
        if value is not None:
            _set_form_initial_value(form, data, key, value)
            if key in form.base_fields and value != []:
                field = form.base_fields[key]
                func = field_func.get(field.__class__, None)
                if func is not None:
                    _set_form_initial_value(form, data, key, func(value))


def get_adminform_initials(response) -> dict:
    context = response.context or response.context_data
    form = context['adminform'].form
    data = {}
    get_form_initials(form, data)
    if 'inline_admin_formsets' in context:
        for inline_admin_formset in context['inline_admin_formsets']:
            formset = inline_admin_formset.formset
            data[f"{formset.prefix}-TOTAL_FORMS"] = str(formset.total_form_count())
            data[f"{formset.prefix}-INITIAL_FORMS"] = str(formset.initial_form_count())

            for form in formset:
                get_form_initials(form, data)
                data[f"{form.prefix}-id"] = str(form.instance.id)

    return data


def _set_form_initial_value(form, data: dict, key:str, value) -> None:
    if form.prefix:
        data[f"{form.prefix}-{key}"] = value
    else:
        data[key] = value
