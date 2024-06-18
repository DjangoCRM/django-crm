from typing import Union
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.core import mail
from django.template import Context
from django.template.defaultfilters import linebreaks
from django.template import Template
from django.template import RequestContext
from django.utils.html import strip_tags

from crm.models.crmemail import CrmEmail
from massmail.models import EmlMessage
from massmail.backends.smtp import OAuth2EmailBackend
from massmail.models.email_account import EmailAccount

prev_corr_blockquote = '<blockquote style="padding-left:1ex; border-left:#ccc 1px' \
                ' solid; margin:0px 0px 0px 0.8ex">{}</blockquote>'


def email_creator(eml_message: Union[CrmEmail, EmlMessage],
                  email_account: EmailAccount,
                  to: list, cc: list = None, bcc: list = None,
                  extra_context: dict = None, force_multipart: bool = False,
                  inline_images: bool = False
                  ) -> Union[EmailMultiAlternatives, EmailMessage]:
    extra_context = extra_context or {}
    extra_context = Context(extra_context)
    tmpl = Template(eml_message.subject)
    subject = tmpl.render(extra_context)
    signature = eml_message.signature.content if eml_message.signature else ''
    tmpl = Template(
        "{% load mailbuilder %}"
        + linebreaks(eml_message.content)
        + "<p> </p>"
        + signature
        + "<p> </p>" + "<p> </p>"
        + "<p>-----------------</p>"
        + prev_corr_blockquote.format(linebreaks(eml_message.prev_corr))
    )
    # extra_context.bind_template(tmpl)    # it doesn't work
    html_content = tmpl.render(extra_context)
    data = _get_data(html_content, to, email_account, subject)
    if cc:
        data['cc'] = cc
    if bcc:
        data['bcc'] = bcc
    if getattr(eml_message, 'read_receipt', False):
        data['headers'] = {
            "Disposition-Notification-To": email_account.from_email,
        }

    return _get_msg(force_multipart, html_content, data, 
             inline_images, extra_context, eml_message)


def create_test_email(request: WSGIRequest, message_id: int,
                      email_account: EmailAccount, to: list,
                      extra_context: dict = None,
                      force_multipart: bool = False,
                      inline_images: bool = False
                      ) -> Union[EmailMultiAlternatives, EmailMessage]:
    extra_context = extra_context or {}
    extra_context = RequestContext(request, extra_context)
    eml_message = EmlMessage.objects.get(id=message_id)
    tmpl = Template(eml_message.subject)
    subject = tmpl.render(extra_context)
    signature = eml_message.signature
    signature_content = signature.content if signature else ''
    tmpl = Template("{% load mailbuilder %}" + eml_message.content + "<p> </p>" + signature_content)
    # extra_context.bind_template(tmpl)    # it doesn't work
    html_content = tmpl.render(extra_context)
    data = _get_data(html_content, to, email_account, subject)

    return _get_msg(force_multipart, html_content, data, 
             inline_images, extra_context, eml_message)


def _get_data(html_content, to, email_account, subject) -> dict:
    body = strip_tags(html_content)
    return {
        'to': to,
        'from_email': email_account.from_email,
        'subject': subject,
        'body': body,
        'connection': email_connection(email_account)
    }    


def _get_msg(force_multipart, html_content, data, 
             inline_images, extra_context, eml_message) -> EmailMessage:
    if force_multipart or html_content:
        msg = EmailMultiAlternatives(**data)
        if html_content:
            msg.attach_alternative(html_content, 'text/html')
        if inline_images:
            inline_files = []
            for att in extra_context.get('cid', []):
                msg.attach(att)
                inline_files.append(att.get_filename())
        files = eml_message.files.all()
        if files and inline_files:
            for f in inline_files:
                files = files.exclude(file=f)
        if files:
            for f in files:
                msg.attach_file(settings.MEDIA_ROOT / f.file.name)
    else:
        msg = EmailMessage(**data)
    return msg


def email_connection(email_account: EmailAccount):
    if email_account.refresh_token:
        connection = OAuth2EmailBackend(refresh_token=email_account.refresh_token)
    else:
        connection = mail.get_connection()
        connection.password = email_account.email_app_password or email_account.email_host_password
        connection.use_tls = email_account.email_use_tls
        connection.use_ssl = email_account.email_use_ssl
    connection.username = email_account.email_host_user
    connection.host = email_account.email_host
    connection.port = email_account.email_port
    return connection
