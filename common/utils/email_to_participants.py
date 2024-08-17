from typing import List
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import loader
from django.utils.translation import override

from common.utils.helpers import send_crm_email


def email_to_participants(obj, subject: str, recipient_list: List[User],
                          responsible: User =None) -> None:
    
    template = loader.get_template("common/notice_participants_email.html")
    site = Site.objects.get_current()
    context = {'obj': obj, 'domain': site.domain, 'responsible': responsible}
    # with override(language_code):
    html_message = template.render(context)

    to = [u.email for u in recipient_list]
    send_crm_email(subject, html_message, to)
