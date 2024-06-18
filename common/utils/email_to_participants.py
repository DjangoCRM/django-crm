from django.contrib.sites.models import Site
from django.template import loader

from common.utils.helpers import send_crm_email


def email_to_participants(obj, subject: str, recipient_list: list, responsible=None) -> None:
    
    template = loader.get_template("common/notice_participants_email.html")
    site = Site.objects.get_current()
    context = {'obj': obj, 'domain': site.domain, 'responsible': responsible}
    html_message = template.render(context)

    send_crm_email(subject, html_message, recipient_list)
