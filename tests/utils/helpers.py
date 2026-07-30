from email.message import EmailMessage
from email.utils import format_datetime
from random import random
from typing import Tuple

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from common.utils.adminform_helpers import (
    get_adminform_initials,
    get_form_initials,
)
from common.utils.helpers import USER_MODEL
from crm.models import Country

__all__ = [
    'add_file_to_form',
    'attach_file_to_email_msg',
    'get_adminform_initials',
    'get_content_file',
    'get_country_instance',
    'get_email_message',
    'get_form_initials',
    'get_random_file_name',
    'get_txt_inmemoryfile',
    'get_user',
]


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


def get_random_file_name() -> str:
    return f'test_file{int(random() * 1E5)}.txt'


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
