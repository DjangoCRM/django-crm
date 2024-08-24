from typing import List
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import loader
from django.utils.translation import gettext as _
from django.utils.translation import override

from common.utils.helpers import compose_subject
from common.utils.helpers import send_crm_email


def email_to_participants(obj, subject: str, recipient_list: List[User],
                          composed_subject: str = '', responsible: User =None) -> None:
    
    template = loader.get_template("common/notice_participants_email.html")
    site = Site.objects.get_current()
    context = {'obj': obj, 'domain': site.domain, 'responsible': responsible}
    while recipient_list:
        user = recipient_list.pop()
        to = [user.email]
        code = user.profile.language_code   # NOQA
        with override(code):
            if not composed_subject:
                composed_subject = compose_subject(obj, _(subject))
            html_message = template.render(context)
        temp_list = []
        while recipient_list:
            u = recipient_list.pop()
            if u.profile.language_code == code: # NOQA
                to.append(u.email)
            else:
                temp_list.append(u)
        send_crm_email(composed_subject, html_message, to)
        recipient_list.extend(temp_list)
